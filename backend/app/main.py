from contextlib import asynccontextmanager
from io import BytesIO
from typing import Literal

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .data_loader import get_dashboard_stats, get_dataset_preview, get_transactions_by_person, get_unique_persons
from .model_loader import clear_model_cache, get_model, predict_batch, predict_batch_with_proba, predict_fraud
from .trainer import train_on_upload


class PredictRequest(BaseModel):
    type: Literal["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT"]
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload model on startup (optional, or lazy on first request)
    try:
        from .model_loader import get_model
        get_model()
    except FileNotFoundError:
        pass
    yield


app = FastAPI(
    title="Fraud Detection API",
    description="Backend for Financial Fraud Monitoring",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/model-info")
def model_info():
    """Return whether a trained model is loaded and ready for predictions."""
    try:
        get_model()
        return {"trained": True, "message": "Logistic Regression model is loaded and ready."}
    except FileNotFoundError:
        return {"trained": False, "message": "No model found. Upload and train a CSV/Excel file first."}


@app.post("/api/train")
async def train_model(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file with columns: type, amount, oldbalanceOrg, newbalanceOrig,
    oldbalanceDest, newbalanceDest, isFraud. Trains Logistic Regression and saves the model.
    All subsequent predictions use this model. Returns training metrics.
    """
    if not file.filename:
        raise HTTPException(400, "No file provided")
    ext = file.filename.lower().split(".")[-1]
    if ext not in ("csv", "xlsx", "xls"):
        raise HTTPException(400, "File must be CSV or Excel (.csv, .xlsx, .xls)")
    try:
        content = await file.read()
        result = train_on_upload(content, file.filename)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/dashboard/stats")
def dashboard_stats():
    return get_dashboard_stats()


@app.get("/api/dataset")
def dataset_preview(limit: int = 100):
    if limit < 1 or limit > 1000:
        limit = 100
    return get_dataset_preview(limit=limit)


@app.get("/api/persons")
def list_persons(limit: int = 500):
    """Return unique persons/accounts from the CSV (id = nameOrig, name = personName if column exists else id)."""
    if limit < 1 or limit > 2000:
        limit = 500
    return {"persons": get_unique_persons(limit=limit)}


@app.post("/api/predict")
def predict(req: PredictRequest):
    pred, proba = predict_fraud(
        type=req.type,
        amount=req.amount,
        oldbalanceOrg=req.oldbalanceOrg,
        newbalanceOrig=req.newbalanceOrig,
        oldbalanceDest=req.oldbalanceDest,
        newbalanceDest=req.newbalanceDest,
    )
    risk = "low" if proba < 0.3 else "medium" if proba < 0.7 else "high"
    return {
        "prediction": pred,
        "fraud_probability": round(proba, 4),
        "fraud_risk_pct": round(proba * 100, 2),
        "risk_level": risk,
    }


@app.get("/api/person/{name_orig}/transactions")
def person_fraud_check(name_orig: str, limit: int = 200):
    """
    Fraud detection for a particular person (sender account).
    Uses the Logistic Regression (linear) model to score each transaction.
    Returns transactions with per-transaction fraud probability and overall person risk.
    """
    if limit < 1 or limit > 500:
        limit = 200
    transactions = get_transactions_by_person(name_orig, max_transactions=limit)
    if not transactions:
        raise HTTPException(404, f"No transactions found for person/account: {name_orig}")

    model_cols = ["type", "amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
    df = pd.DataFrame(transactions)[model_cols]
    predictions = predict_batch_with_proba(df)

    out_transactions = []
    for i, row in enumerate(transactions):
        pred, proba = predictions[i]
        out_transactions.append({
            **row,
            "fraud_prediction": pred,
            "fraud_probability": round(proba, 4),
            "fraud_risk_pct": round(proba * 100, 2),
            "risk_level": "low" if proba < 0.3 else "medium" if proba < 0.7 else "high",
        })

    # Overall person risk: max fraud probability (worst transaction) and mean
    probas = [p[1] for p in predictions]
    max_proba = max(probas)
    mean_proba = sum(probas) / len(probas)
    overall_risk = "low" if max_proba < 0.3 else "medium" if max_proba < 0.7 else "high"

    return {
        "person_id": name_orig,
        "person_name": name_orig,
        "transaction_count": len(out_transactions),
        "overall_risk_level": overall_risk,
        "max_fraud_risk_pct": round(max_proba * 100, 2),
        "mean_fraud_risk_pct": round(mean_proba * 100, 2),
        "model_info": "Logistic Regression (linear model for binary fraud classification)",
        "transactions": out_transactions,
    }


@app.post("/api/predict-batch")
async def predict_batch_upload(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Upload a CSV file")
    try:
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))
        required = ["type", "amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise HTTPException(400, f"CSV must have columns: {required}. Missing: {missing}")
        df = df[required]
        predictions = predict_batch(df)
        df = df.copy()
        df["Fraud Prediction"] = predictions
        return df.fillna("").to_dict(orient="records")
    except Exception as e:
        raise HTTPException(400, str(e))
