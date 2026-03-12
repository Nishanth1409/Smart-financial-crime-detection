"""Load and run the fraud detection model."""
import os
from pathlib import Path

import joblib
import pandas as pd

_MODEL = None
_MODEL_PATH = os.environ.get("MODEL_PATH", "fraud_detection_pipeline.pkl")

# Resolve path: backend/app -> project root (Smart-financial-crime-detection, where .pkl and CSV live)
_ROOT = Path(__file__).resolve().parent.parent.parent


def clear_model_cache():
    """Clear cached model so next request loads from disk (e.g. after retrain)."""
    global _MODEL
    _MODEL = None


def get_model():
    global _MODEL
    if _MODEL is None:
        path = Path(_MODEL_PATH)
        if not path.is_absolute():
            path = _ROOT / path
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")
        _MODEL = joblib.load(path)
    return _MODEL


def predict_fraud(
    type: str,
    amount: float,
    oldbalanceOrg: float,
    newbalanceOrig: float,
    oldbalanceDest: float,
    newbalanceDest: float,
) -> tuple[int, float]:
    """Return (prediction 0/1, fraud_probability)."""
    model = get_model()
    df = pd.DataFrame([{
        "type": type,
        "amount": amount,
        "oldbalanceOrg": oldbalanceOrg,
        "newbalanceOrig": newbalanceOrig,
        "oldbalanceDest": oldbalanceDest,
        "newbalanceDest": newbalanceDest,
    }])
    pred = model.predict(df)[0]
    proba = model.predict_proba(df)[0][1]
    return int(pred), float(proba)


def predict_batch(df: pd.DataFrame) -> list[int]:
    """Predict for multiple rows. DataFrame must have required columns."""
    model = get_model()
    return model.predict(df).tolist()


def predict_batch_with_proba(df: pd.DataFrame) -> list[tuple[int, float]]:
    """Predict for multiple rows; returns list of (prediction, fraud_probability)."""
    model = get_model()
    preds = model.predict(df)
    probas = model.predict_proba(df)[:, 1]  # P(fraud)
    return [(int(p), float(pr)) for p, pr in zip(preds, probas)]
