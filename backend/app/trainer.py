"""
Train Logistic Regression fraud detection model on uploaded CSV or Excel.
Pipeline: ColumnTransformer (StandardScaler + OneHotEncoder) + LogisticRegression.
"""
import os
from io import BytesIO
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .model_loader import clear_model_cache

_ROOT = Path(__file__).resolve().parent.parent.parent
_MODEL_PATH = os.environ.get("MODEL_PATH", "fraud_detection_pipeline.pkl")

REQUIRED_COLUMNS = ["type", "amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest", "isFraud"]
CATEGORICAL = ["type"]
NUMERIC = ["amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: strip; map to exact names expected by pipeline."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    # Lowercase map for flexible matching, then standard names
    lower_to_standard = {
        "type": "type",
        "amount": "amount",
        "oldbalanceorg": "oldbalanceOrg",
        "newbalanceorig": "newbalanceOrig",
        "oldbalancedest": "oldbalanceDest",
        "newbalancedest": "newbalanceDest",
        "isfraud": "isFraud",
        "transaction_type": "type",
    }
    rename_map = {}
    for col in df.columns:
        key = col.lower()
        if key in lower_to_standard:
            rename_map[col] = lower_to_standard[key]
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def _read_upload(content: bytes, filename: str) -> pd.DataFrame:
    """Read CSV or Excel from uploaded file content."""
    fn = (filename or "").lower()
    if fn.endswith(".csv"):
        return pd.read_csv(BytesIO(content))
    if fn.endswith(".xlsx"):
        return pd.read_excel(BytesIO(content), engine="openpyxl")
    if fn.endswith(".xls"):
        return pd.read_excel(BytesIO(content))
    raise ValueError("File must be CSV or Excel (.csv, .xlsx, .xls)")


def train_on_upload(content: bytes, filename: str) -> dict:
    """
    Train Logistic Regression on uploaded CSV/Excel. Saves pipeline to MODEL_PATH.
    Returns dict with metrics and sample info. Clears model cache so next predict uses new model.
    """
    df = _read_upload(content, filename)
    df = _normalize_columns(df)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Required: {REQUIRED_COLUMNS}")

    df = df[REQUIRED_COLUMNS].copy()
    df = df.dropna()
    if len(df) < 100:
        raise ValueError("Need at least 100 rows after dropping missing values")

    y = df["isFraud"]
    X = df.drop(columns=["isFraud"])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(drop="first"), CATEGORICAL),
        ],
        remainder="drop",
    )
    pipeline = Pipeline([
        ("prep", preprocessor),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)),
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    accuracy = round(float(accuracy_score(y_test, y_pred)), 4)
    precision = round(float(precision_score(y_test, y_pred, zero_division=0)), 4)
    recall = round(float(recall_score(y_test, y_pred, zero_division=0)), 4)
    f1 = round(float(f1_score(y_test, y_pred, zero_division=0)), 4)

    path = Path(_MODEL_PATH)
    if not path.is_absolute():
        path = _ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)

    clear_model_cache()

    df_preview = df.head(100).copy()
    df_preview["Fraud Prediction"] = pipeline.predict(X.head(100))
    preview = df_preview.fillna("").to_dict(orient="records")

    return {
        "status": "success",
        "message": "Model trained and saved. All predictions will use this model.",
        "filename": filename,
        "total_rows": len(df),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "fraud_count": int(y.sum()),
        "non_fraud_count": int((y == 0).sum()),
        "preview": preview,
    }
