FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

# Model and data are mounted at runtime via docker-compose (e.g. MODEL_PATH, DATA_PATH)
ENV MODEL_PATH=/data/fraud_detection_pipeline.pkl
ENV DATA_PATH=/data/AIML Dataset.csv

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
