# Smart Financial Crime Detection

A full-stack **fraud detection** app with a React dashboard and FastAPI backend. Train a Logistic Regression model on your transaction data, view analytics, and run single or batch predictions.

## Features

- **Dashboard** — Fraud vs normal counts, transaction types, daily/weekly trends (ECharts).
- **Predict** — Single-transaction prediction with fraud probability and risk level.
- **Explorer** — Dataset preview and **train model** on uploaded CSV/Excel.
- **By Person** — Look up transactions by account and see per-transaction fraud scores.

## Tech Stack

| Layer    | Stack |
|----------|--------|
| Backend  | FastAPI, uvicorn, pandas, scikit-learn |
| Frontend | React 18, Vite, React Router, ECharts |
| Model    | Logistic Regression (see [ML_MODEL.md](ML_MODEL.md)) |

## Prerequisites

- **Python 3.10+** (backend)
- **Node.js 18+** (frontend)

## Quick Start (local)

**1. Backend** (from project root):

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**2. Frontend** (new terminal):

```bash
cd frontend
npm install
npm run dev
```

**3. Open** [http://localhost:3000](http://localhost:3000). The frontend proxies `/api` to the backend at port 8000.

### Data & model

- **Dashboard / Explorer / By Person** use the dataset at project root. Set `DATA_PATH` to your CSV path (default: `AIML Dataset_with_person_name.csv`). If the file is missing, dashboard shows empty stats.
- **Predict** requires a trained model. Either:
  - Put `fraud_detection_pipeline.pkl` at project root (e.g. from `scripts/train_fraud_model.py`), or  
  - Use **Explorer** → upload a CSV/Excel with columns `type`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`, `isFraud` and train.

See [ML_MODEL.md](ML_MODEL.md) for training options and [DEPLOYMENT.md](DEPLOYMENT.md) for Docker and cloud deployment.

## Project Structure

```
Smart-financial-crime-detection/
├── backend/
│   ├── app/
│   │   ├── main.py       # FastAPI app, routes
│   │   ├── data_loader.py
│   │   ├── model_loader.py
│   │   └── trainer.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── pages/        # Dashboard, Predict, Explorer, PersonFraud
│   │   └── components/   # ECharts wrappers
│   ├── package.json
│   └── Dockerfile
├── scripts/
│   ├── train_fraud_model.py
│   ├── generate_sample_datasets.py
│   └── add_person_name_to_csv.py
├── sample_datasets/       # Small CSVs for demos
├── docker-compose.yml
├── ML_MODEL.md
└── DEPLOYMENT.md
```

## API

- **Health:** `GET /health`
- **Docs:** [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- **Train:** `POST /api/train` (CSV/Excel upload)
- **Predict:** `POST /api/predict`, `POST /api/predict-batch`
- **Dashboard:** `GET /api/dashboard/stats`, `GET /api/dataset`, `GET /api/persons`, `GET /api/person/{nameOrig}/transactions`

## Docker

From project root (with dataset and optional `fraud_detection_pipeline.pkl` in place):

```bash
docker compose up -d --build
```

Frontend: http://localhost | Backend: http://localhost:8000

Details: [DEPLOYMENT.md](DEPLOYMENT.md).
