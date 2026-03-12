# Fraud Detection App – Deployment Guide

This app runs as **FastAPI (backend) + React (frontend)**. You can run it locally, with Docker, or on AWS / GCP / Azure.

---

## Quick start (local, no Docker)

**Backend (Python 3.10+)**

From **Smart-financial-crime-detection** (project root; contains `backend/`, `frontend/`, `fraud_detection_pipeline.pkl`, and dataset CSV):

```bash
cd Smart-financial-crime-detection/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 (frontend). The dev server proxies `/api` to the backend. Set `VITE_API_URL=http://localhost:8000` if the backend runs on another host.

---

## Docker (local or any VM)

From the **project root** (where `docker-compose.yml` and `AIML Dataset.csv` / `fraud_detection_pipeline.pkl` are):

```bash
docker compose up -d --build
```

- Frontend: http://localhost (port 80)  
- Backend API: http://localhost:8000  
- API docs: http://localhost:8000/docs  

Data and model are mounted from the host; no need to bake the large CSV into the image.

**Optional:** To speed up dashboard stats with a large CSV, set in `docker-compose.yml`:

```yaml
environment:
  - SAMPLE_ROWS=100000
```

---

## Cloud deployment options

### AWS

1. **ECS (Fargate)**  
   - Build and push backend and frontend images to **ECR**.  
   - Run two tasks (backend + frontend) or one task with both (e.g. frontend container + backend container).  
   - Put **ALB** in front; route `/api` and `/health` to the backend target and `/` to the frontend (or use a single nginx container that proxies to backend).  
   - Store `fraud_detection_pipeline.pkl` and optionally a sample CSV in **S3**; at startup the backend can download them (or mount EFS if you prefer).

2. **App Runner**  
   - Deploy backend and frontend as two services.  
   - Point the frontend’s `VITE_API_URL` to the backend App Runner URL.  
   - Use a custom domain and/or VPC if needed.

3. **EC2**  
   - One EC2 instance: install Docker, clone repo, run `docker compose up -d`.  
   - Open ports 80 and 8000 in the security group; use the instance public IP.  
   - For HTTPS, put **CloudFront** or **ALB** in front and terminate SSL there.

### GCP

1. **Cloud Run**  
   - Build and push images to **Artifact Registry**.  
   - Deploy backend and frontend as two Cloud Run services.  
   - Set the frontend’s `VITE_API_URL` to the backend Cloud Run URL.  
   - For the large CSV/model, use **Cloud Storage** and have the backend download at startup, or use a small sample and env `DATA_PATH`/`MODEL_PATH` pointing to a GCS path if you add GCS support in code.

2. **GCE VM**  
   - Same as EC2: Docker + `docker compose up -d` on a VM; open HTTP/HTTPS and 8000 as needed.

### Azure

1. **Container Apps**  
   - Push images to **ACR** (Azure Container Registry).  
   - Create two Container Apps (backend + frontend).  
   - Set `VITE_API_URL` in the frontend build to the backend Container App URL.  
   - Use **Azure Blob** for model/CSV and optional startup download in the backend.

2. **Azure VM**  
   - Run Docker and `docker compose up -d` on a Linux VM; use NSG rules to expose 80/8000 and optionally put **Application Gateway** in front for HTTPS.

---

## Environment variables

| Variable        | Where     | Description |
|----------------|-----------|-------------|
| `MODEL_PATH`   | Backend   | Path to `fraud_detection_pipeline.pkl` (absolute or relative to app root). |
| `DATA_PATH`    | Backend   | Path to `AIML Dataset.csv` for dashboard and explorer. |
| `SAMPLE_ROWS`  | Backend   | If set to a positive integer, only that many rows are used for dashboard stats (faster for huge CSVs). `0` = use full file. |
| `VITE_API_URL` | Frontend  | Backend base URL (e.g. `https://api.yoursite.com`). Leave empty when same origin (e.g. nginx proxying `/api`). |

---

## Production checklist

- Use **HTTPS** (ALB/CloudFront/App Gateway/Cloud Run default).
- Restrict **CORS** in FastAPI to your frontend origin(s).
- Run backend with **multiple workers** if needed:  
  `uvicorn app.main:app --host 0.0.0.0 --workers 2`
- For very large datasets, consider **caching** dashboard stats (e.g. Redis) or precomputing and serving static JSON.
- Keep **secrets** (API keys, DB URLs if added) in the platform’s secret manager (Secrets Manager, Secret Manager, Key Vault) and inject via env.
