Sample datasets for fraud detection (same structure as the main project CSV).

Files: fraud_dataset_01.csv ... fraud_dataset_10.csv
Each has 5,000 rows with different synthetic data. Columns match the project dataset:
  step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig, nameDest,
  oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud, personName

How to use:
  - Open the website → Explorer → "Train model on new dataset"
  - Choose any of these CSV files and click "Upload file"
  - The model will be trained on that dataset and used for all predictions

To regenerate these files, from project root run:
  python scripts/generate_sample_datasets.py
