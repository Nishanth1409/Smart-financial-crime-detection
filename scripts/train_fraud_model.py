"""
Train the fraud detection model in this project. The model is saved to fraud_detection_pipeline.pkl
and used by the backend for all predictions. Whenever you provide a new dataset, train on it to
update the model.

Run from project root:
  python scripts/train_fraud_model.py                    # use default project CSV
  python scripts/train_fraud_model.py --data path/to/new_dataset.csv   # train on your new dataset
  python scripts/train_fraud_model.py --data my.csv --sample 100000    # new dataset, first 100k rows
"""
import argparse
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "fraud_detection_pipeline.pkl"

# Default datasets if --data not given
DATA_FILES = ["AIML Dataset_with_person_name.csv", "AIML Dataset.csv"]

REQUIRED = ["type", "amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest", "isFraud"]
CATEGORICAL = ["type"]
NUMERIC = ["amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]


def main():
    parser = argparse.ArgumentParser(
        description="Train the fraud detection model on a dataset. Model is saved and used by the app."
    )
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Path to your CSV dataset (required columns: type, amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest, isFraud). If not set, uses default project CSV.",
    )
    parser.add_argument("--sample", type=int, default=None, help="Use first N rows only (default: all)")
    args = parser.parse_args()

    data_path = None
    if args.data:
        p = Path(args.data)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        if not p.exists():
            print(f"Error: Dataset not found: {p}")
            sys.exit(1)
        data_path = p
    else:
        for name in DATA_FILES:
            p = PROJECT_ROOT / name
            if p.exists():
                data_path = p
                break
        if not data_path:
            print(f"Error: No dataset found. Use --data path/to/your.csv or place one of {DATA_FILES} in project root.")
            sys.exit(1)

    print(f"Training model on: {data_path}" + (f" (first {args.sample:,} rows)" if args.sample else " (all rows)"))
    df = pd.read_csv(data_path, nrows=args.sample)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        print(f"Error: Dataset missing columns: {missing}. Required: {REQUIRED}")
        sys.exit(1)

    df = df[REQUIRED].copy().dropna()
    if len(df) < 100:
        print("Error: Need at least 100 rows after dropping missing values.")
        sys.exit(1)

    print(f"Rows: {len(df):,}  Fraud: {df['isFraud'].sum():,}  Non-fraud: {(df['isFraud'] == 0).sum():,}")

    y = df["isFraud"]
    X = df.drop(columns=["isFraud"])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)

    pipeline = Pipeline([
        ("prep", ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), NUMERIC),
                ("cat", OneHotEncoder(drop="first"), CATEGORICAL),
            ],
            remainder="drop",
        )),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)),
    ])

    print("Training Logistic Regression...")
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nModel saved: {MODEL_PATH}")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 score:  {f1:.4f}")
    print("\nModel trained and saved. All predictions in this project will use this model until you train on a new dataset.")


if __name__ == "__main__":
    main()
