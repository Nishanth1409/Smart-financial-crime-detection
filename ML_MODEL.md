# ML Model – Fraud Detection

The model is **trained in this project** and is **retrained whenever you provide a new dataset**. Training happens here (not elsewhere); the saved model is then used for all predictions until you train on another dataset.

- **New dataset via app:** Explorer → upload your CSV/Excel → click “Upload file”. The model is trained on that data and saved; Predict and By Person use it immediately.
- **New dataset via script:** `python scripts/train_fraud_model.py --data path/to/your.csv` (or use the default project CSV without `--data`).

This project uses a **Logistic Regression** model for binary fraud classification.

## Model

- **Type:** Logistic Regression (linear model)
- **Pipeline:** `ColumnTransformer` (StandardScaler for numeric features + OneHotEncoder for `type`) → `LogisticRegression(class_weight="balanced", max_iter=1000)`
- **Features:** `type`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`
- **Target:** `isFraud` (0 or 1)
- **Saved as:** `fraud_detection_pipeline.pkl` (project root)

## How to train on a new dataset

**Option 1 – In the app (Explorer)**  
1. Open the **Explorer** page.  
2. Under “Train model on new dataset”, choose your CSV or Excel file (columns: `type`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`, `isFraud`).  
3. Click **Upload file**.  
4. The model is trained on your data and saved; all Predict and By Person results use this model until you train on another dataset.

**Option 2 – Script (your own CSV or project default)**  
From project root:

```bash
# Train on a new dataset you provide
python scripts/train_fraud_model.py --data path/to/your_new_dataset.csv

# Optional: use only first N rows (faster for large files)
python scripts/train_fraud_model.py --data path/to/your_new_dataset.csv --sample 100000

# Train on default project CSV (no --data)
python scripts/train_fraud_model.py
python scripts/train_fraud_model.py --sample 100000
```

Without `--data`, the script uses `AIML Dataset_with_person_name.csv` or `AIML Dataset.csv` from the project root.

## Integration (how the model is used)

| Part | Role |
|------|------|
| **Model file** | `fraud_detection_pipeline.pkl` in **Smart-financial-crime-detection** (same folder as `backend/`, `frontend/`). |
| **Backend** | `Smart-financial-crime-detection/backend/app/model_loader.py` loads the `.pkl` on first prediction (or at startup). Path is project root; overridable with env `MODEL_PATH`. |
| **Training** | `backend/app/trainer.py` (inside Smart-financial-crime-detection) trains on CSV/Excel upload, saves to the same `.pkl`, and clears the in-memory model so the next request uses the new model. |
| **API** | `POST /api/predict` (single), `POST /api/predict-batch` (CSV), `GET /api/person/{id}/transactions` (per-account scores), `POST /api/train` (upload + train). |
| **Frontend** | **Predict** page → single transaction; **By Person** → per-account fraud risk; **Explorer** → upload CSV to train and see preview with predictions. |

If the `.pkl` file is missing, the app still starts; Predict/By Person will fail until you train via Explorer or run `python scripts/train_fraud_model.py` from the project root.
