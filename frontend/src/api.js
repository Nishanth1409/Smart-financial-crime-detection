const API_BASE = import.meta.env.VITE_API_URL || '';

export async function getDashboardStats() {
  const r = await fetch(`${API_BASE}/api/dashboard/stats`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function getDatasetPreview(limit = 100) {
  const r = await fetch(`${API_BASE}/api/dataset?limit=${limit}`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function predictTransaction(data) {
  const r = await fetch(`${API_BASE}/api/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function predictBatch(file) {
  const form = new FormData();
  form.append('file', file);
  const r = await fetch(`${API_BASE}/api/predict-batch`, {
    method: 'POST',
    body: form,
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

/** Check if model is trained and ready. */
export async function getModelInfo() {
  const r = await fetch(`${API_BASE}/api/model-info`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

/** Upload CSV or Excel and train Logistic Regression model. Returns metrics. */
export async function trainModel(file) {
  const form = new FormData();
  form.append('file', file);
  const r = await fetch(`${API_BASE}/api/train`, { method: 'POST', body: form });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(text || 'Training failed');
  }
  return r.json();
}

/** Load list of persons/accounts from CSV (id + name). */
export async function getPersons(limit = 500) {
  const r = await fetch(`${API_BASE}/api/persons?limit=${limit}`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

/** Fraud detection for a particular person (sender account). Uses Logistic Regression (linear) model. */
export async function getPersonFraud(nameOrig, limit = 200) {
  const r = await fetch(`${API_BASE}/api/person/${encodeURIComponent(nameOrig)}/transactions?limit=${limit}`);
  if (!r.ok) {
    const text = await r.text();
    if (r.status === 404) throw new Error(text || 'No transactions found for this person');
    throw new Error(text);
  }
  return r.json();
}
