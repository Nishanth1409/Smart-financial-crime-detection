"""Load and cache dataset stats for dashboard. Uses optional sampling for large files."""
import os
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent.parent
_DATA_PATH = os.environ.get("DATA_PATH", "AIML Dataset_with_person_name.csv")
_SAMPLE_ROWS = int(os.environ.get("SAMPLE_ROWS", "0"))  # 0 = load all (may be slow for 6M+ rows)

_cached_stats = None


def _data_path() -> Path:
    p = Path(_DATA_PATH)
    return _ROOT / p if not p.is_absolute() else p


def get_dashboard_stats():
    """Load dataset (or sample) and compute stats. Cached after first call."""
    global _cached_stats
    if _cached_stats is not None:
        return _cached_stats

    path = _data_path()
    if not path.exists():
        return {
            "total_transactions": 0,
            "fraud_cases": 0,
            "fraud_rate_pct": 0.0,
            "normal_transactions": 0,
            "fraud_vs_normal": [],
            "transaction_types": [],
            "amount_sample": [],
            "fraud_by_type": [],
            "daily_fraud": [],
            "weekly_fraud": [],
        }

    nrows = _SAMPLE_ROWS if _SAMPLE_ROWS > 0 else None
    df = pd.read_csv(path, nrows=nrows)

    fraud_sum = int(df["isFraud"].sum())
    total = len(df)
    fraud_rate = (df["isFraud"].mean() * 100) if total else 0.0

    fraud_vs_normal = df["isFraud"].value_counts().sort_index()
    fraud_vs_normal_list = [{"label": str(k), "count": int(v)} for k, v in fraud_vs_normal.items()]

    type_counts = df["type"].value_counts()
    transaction_types = [{"type": k, "count": int(v)} for k, v in type_counts.items()]

    amount_sample = df["amount"].head(1000).fillna(0).tolist()

    fraud_by_type = df.groupby("type", as_index=False)["isFraud"].sum()
    fraud_by_type_list = [{"type": row["type"], "fraud_count": int(row["isFraud"])} for _, row in fraud_by_type.iterrows()]

    # Daily: by step (day). Fraud = isFraud 1 (≥50%), Not fraud = isFraud 0 (<50%)
    daily_fraud = []
    if "step" in df.columns:
        daily_agg = df.groupby("step", as_index=False).agg(
            fraud_count=("isFraud", "sum"),
            total=("isFraud", "count"),
        )
        daily_agg["not_fraud_count"] = daily_agg["total"] - daily_agg["fraud_count"]
        daily_agg["fraud_pct"] = (daily_agg["fraud_count"] / daily_agg["total"].replace(0, 1) * 100).round(2)
        daily_fraud = [
            {
                "day": int(row["step"]),
                "fraud_count": int(row["fraud_count"]),
                "not_fraud_count": int(row["not_fraud_count"]),
                "total": int(row["total"]),
                "fraud_pct": float(row["fraud_pct"]),
            }
            for _, row in daily_agg.iterrows()
        ]
        daily_fraud.sort(key=lambda x: x["day"])

    # Weekly: group steps by week (step // 7)
    weekly_fraud = []
    if "step" in df.columns:
        df_week = df.copy()
        df_week["week"] = (df_week["step"] // 7) + 1
        weekly_agg = df_week.groupby("week", as_index=False).agg(
            fraud_count=("isFraud", "sum"),
            total=("isFraud", "count"),
        )
        weekly_agg["not_fraud_count"] = weekly_agg["total"] - weekly_agg["fraud_count"]
        weekly_agg["fraud_pct"] = (weekly_agg["fraud_count"] / weekly_agg["total"].replace(0, 1) * 100).round(2)
        weekly_fraud = [
            {
                "week": int(row["week"]),
                "fraud_count": int(row["fraud_count"]),
                "not_fraud_count": int(row["not_fraud_count"]),
                "total": int(row["total"]),
                "fraud_pct": float(row["fraud_pct"]),
            }
            for _, row in weekly_agg.iterrows()
        ]
        weekly_fraud.sort(key=lambda x: x["week"])

    _cached_stats = {
        "total_transactions": total,
        "fraud_cases": fraud_sum,
        "fraud_rate_pct": round(fraud_rate, 2),
        "normal_transactions": int(total - fraud_sum),
        "fraud_vs_normal": fraud_vs_normal_list,
        "transaction_types": transaction_types,
        "amount_sample": amount_sample,
        "fraud_by_type": fraud_by_type_list,
        "daily_fraud": daily_fraud,
        "weekly_fraud": weekly_fraud,
    }
    return _cached_stats


def get_dataset_preview(limit: int = 100) -> list[dict]:
    """Return first `limit` rows as list of dicts for explorer."""
    path = _data_path()
    if not path.exists():
        return []
    df = pd.read_csv(path, nrows=limit)
    return df.fillna("").to_dict(orient="records")


def get_unique_persons(limit: int = 500) -> list[dict]:
    """
    Get unique person/account IDs (nameOrig) from the CSV.
    Returns list of { "id": nameOrig, "name": personName }.
    If CSV has a "personName" (or "name") column it is used; otherwise name = id (nameOrig).
    """
    path = _data_path()
    if not path.exists():
        return []

    seen = set()
    out = []
    chunk_size = 100_000
    usecols = ["nameOrig"]
    try:
        first = pd.read_csv(path, nrows=1)
        if "personName" in first.columns:
            usecols = ["nameOrig", "personName"]
        elif "name" in first.columns:
            usecols = ["nameOrig", "name"]
    except Exception:
        pass

    for chunk in pd.read_csv(path, chunksize=chunk_size, usecols=usecols):
        if "nameOrig" not in chunk.columns:
            continue
        for _, row in chunk.iterrows():
            uid = str(row["nameOrig"]).strip()
            if not uid or uid in seen:
                continue
            seen.add(uid)
            name = uid
            if "personName" in chunk.columns and pd.notna(row.get("personName")):
                name = str(row["personName"]).strip() or uid
            elif "name" in chunk.columns and pd.notna(row.get("name")):
                name = str(row["name"]).strip() or uid
            out.append({"id": uid, "name": name})
            if len(out) >= limit:
                return out
    return out


def get_transactions_by_person(name_orig: str, max_transactions: int = 200) -> list[dict]:
    """
    Find all transactions for a given person (sender account nameOrig).
    Reads CSV in chunks to handle large files. Returns up to max_transactions rows.
    """
    path = _data_path()
    if not path.exists():
        return []

    required = ["type", "amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest", "nameOrig", "nameDest", "isFraud"]
    out = []
    chunk_size = 100_000

    cols = [c for c in required + ["step"] if c in required or c == "step"]
    for chunk in pd.read_csv(path, chunksize=chunk_size, usecols=cols):
        # Ensure nameOrig is present (might be nameOrig or similar)
        if "nameOrig" not in chunk.columns:
            continue
        subset = chunk[chunk["nameOrig"].astype(str).str.strip().str.lower() == str(name_orig).strip().lower()]
        for _, row in subset.iterrows():
            out.append({
                "step": int(row.get("step", 0)),
                "type": str(row["type"]),
                "amount": float(row["amount"]),
                "oldbalanceOrg": float(row["oldbalanceOrg"]),
                "newbalanceOrig": float(row["newbalanceOrig"]),
                "oldbalanceDest": float(row["oldbalanceDest"]),
                "newbalanceDest": float(row["newbalanceDest"]),
                "nameOrig": str(row["nameOrig"]),
                "nameDest": str(row["nameDest"]),
                "isFraud": int(row["isFraud"]),
            })
            if len(out) >= max_transactions:
                return out
    return out
