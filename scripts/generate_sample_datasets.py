"""
Generate 10 synthetic fraud-detection CSV datasets with the same structure as the project dataset.
Each file has different random data and can be uploaded in the Explorer to train the model.
Output: sample_datasets/fraud_dataset_01.csv ... fraud_dataset_10.csv
Run from project root: python scripts/generate_sample_datasets.py
"""
import random
from pathlib import Path

import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "sample_datasets"
ROWS_PER_FILE = 5000  # Good size for upload and training
FRAUD_RATE = 0.002  # ~0.2% fraud (realistic)
TYPES = ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT"]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
    "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
]


def make_account_id(prefix: str, i: int) -> str:
    return f"{prefix}{i:07d}"


def make_person_name(seed: int) -> str:
    r = random.Random(seed)
    return f"{r.choice(FIRST_NAMES)} {r.choice(LAST_NAMES)}"


def generate_one_dataset(seed: int) -> pd.DataFrame:
    r = random.Random(seed)
    np.random.seed(seed)

    n = ROWS_PER_FILE
    step = np.arange(1, n + 1, dtype=int)
    type_ = np.array([r.choice(TYPES) for _ in range(n)])
    amount = np.round(np.clip(np.random.lognormal(7, 2, n), 0.01, 1e8), 2)

    # Sender: nameOrig, oldbalanceOrg, newbalanceOrig
    n_orig = max(n // 3, 500)
    orig_ids = [make_account_id("C", i) for i in range(n_orig)]
    name_orig = np.array([r.choice(orig_ids) for _ in range(n)])
    old_org = np.round(np.clip(np.random.lognormal(8, 2, n), 0, 1e9), 2)
    new_org = np.round(old_org - amount + np.where(type_ == "PAYMENT", 0, amount * 0.95), 2)
    new_org = np.clip(new_org, 0, 1e9)

    # Receiver: nameDest, oldbalanceDest, newbalanceDest
    n_dest = max(n // 3, 500)
    dest_ids = [make_account_id("M", i) for i in range(n_dest)]
    name_dest = np.array([r.choice(dest_ids) for _ in range(n)])
    old_dest = np.round(np.clip(np.random.lognormal(7, 2, n), 0, 1e9), 2)
    new_dest = np.round(old_dest + amount * 0.98, 2)
    new_dest = np.clip(new_dest, 0, 1e9)

    # Fraud: small fraction
    is_fraud = np.zeros(n, dtype=int)
    n_fraud = max(1, int(n * FRAUD_RATE))
    fraud_idx = r.sample(range(n), n_fraud)
    is_fraud[fraud_idx] = 1

    is_flagged = np.minimum(is_fraud, np.random.binomial(1, 0.5, n))

    person_name = np.array([make_person_name(hash(str(o)) % (2**31)) for o in name_orig])

    return pd.DataFrame({
        "step": step,
        "type": type_,
        "amount": amount,
        "nameOrig": name_orig,
        "oldbalanceOrg": old_org,
        "newbalanceOrig": new_org,
        "nameDest": name_dest,
        "oldbalanceDest": old_dest,
        "newbalanceDest": new_dest,
        "isFraud": is_fraud,
        "isFlaggedFraud": is_flagged,
        "personName": person_name,
    })


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating 10 datasets in {OUTPUT_DIR} ({ROWS_PER_FILE:,} rows each)...")
    for i in range(1, 11):
        seed = 42 + i * 100
        df = generate_one_dataset(seed)
        path = OUTPUT_DIR / f"fraud_dataset_{i:02d}.csv"
        df.to_csv(path, index=False)
        fraud_count = df["isFraud"].sum()
        print(f"  {path.name}: {len(df):,} rows, {fraud_count} fraud")
    print("Done. Upload any of these CSVs in the Explorer to train the model.")


if __name__ == "__main__":
    main()
