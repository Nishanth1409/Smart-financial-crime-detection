import { useState, useEffect, useRef } from 'react'
import { getDatasetPreview, trainModel } from '../api'

export default function Explorer() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [limit, setLimit] = useState(100)
  const [file, setFile] = useState(null)
  const [trainResult, setTrainResult] = useState(null)
  const [trainLoading, setTrainLoading] = useState(false)
  const [trainError, setTrainError] = useState(null)
  const [fileInputKey, setFileInputKey] = useState(0)
  const fileInputRef = useRef(null)

  useEffect(() => {
    setLoading(true)
    getDatasetPreview(limit)
      .then(setRows)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [limit])

  const handleFileChange = (e) => {
    const f = e.target.files?.[0]
    setFile(f || null)
    setTrainResult(null)
    setTrainError(null)
  }

  const handleRemoveFile = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setFile(null)
    setTrainResult(null)
    setTrainError(null)
    setFileInputKey((k) => k + 1)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleTrainModel = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (!file) return
    setTrainLoading(true)
    setTrainError(null)
    setTrainResult(null)
    try {
      const data = await trainModel(file)
      setTrainResult(data)
    } catch (err) {
      setTrainError(err.message)
    } finally {
      setTrainLoading(false)
    }
  }

  const columns = rows.length ? Object.keys(rows[0]) : []

  return (
    <div className="page-content">
      <h1 className="page-title">Dataset Explorer</h1>
      <p className="page-subtitle">The model is trained in this project. Upload a new dataset (CSV) to train the model on it—all predictions will then use that trained model.</p>

      <div className="card">
        <h3>Preview rows</h3>
        <select value={limit} onChange={(e) => setLimit(Number(e.target.value))} style={{ marginBottom: '1rem', padding: '0.5rem' }}>
          <option value={50}>50</option>
          <option value={100}>100</option>
          <option value={200}>200</option>
          <option value={500}>500</option>
        </select>
        {loading && <div className="loading">Loading…</div>}
        {error && <div className="error">{error}</div>}
        {!loading && !error && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  {columns.map((c) => (
                    <th key={c}>{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr key={i}>
                    {columns.map((col) => (
                      <td key={col}>{String(row[col] ?? '')}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card">
        <h3>Train model on new dataset</h3>
        <p>Upload your CSV (or Excel). The model will be trained on this data and saved; all Predict and By Person results will use this model until you train on another dataset. Required columns: type, amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest, isFraud.</p>
        <div className={`file-upload ${file ? 'has-file' : ''}`}>
          <input
            key={fileInputKey}
            ref={fileInputRef}
            type="file"
            id="train-file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
          />
          <label htmlFor="train-file">{file ? file.name : 'Choose CSV file'}</label>
        </div>
        <div className="upload-actions" style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem', flexWrap: 'wrap', position: 'relative', zIndex: 1 }}>
          <button type="button" className="btn btn-primary" onClick={handleTrainModel} disabled={!file || trainLoading}>
            {trainLoading ? 'Uploading…' : 'Upload file'}
          </button>
          <button type="button" className="btn" onClick={handleRemoveFile} disabled={!file || trainLoading} style={{ border: '1px solid var(--border)' }}>
            Remove CSV
          </button>
        </div>
        {trainError && <div className="error" style={{ marginTop: '1rem' }}>{trainError}</div>}

        {trainResult && trainResult.status === 'success' && (
          <>
            <div className="metrics" style={{ marginTop: '1.5rem' }}>
              <div className="metric">
                <div className="value">{(trainResult.accuracy * 100)?.toFixed(2)}%</div>
                <div className="label">Accuracy</div>
              </div>
              <div className="metric">
                <div className="value">{(trainResult.precision * 100)?.toFixed(2)}%</div>
                <div className="label">Precision</div>
              </div>
              <div className="metric">
                <div className="value">{(trainResult.recall * 100)?.toFixed(2)}%</div>
                <div className="label">Recall</div>
              </div>
              <div className="metric">
                <div className="value">{trainResult.total_rows?.toLocaleString()}</div>
                <div className="label">Rows trained</div>
              </div>
            </div>
            <p style={{ color: 'var(--muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
              {trainResult.message} Fraud: {trainResult.fraud_count?.toLocaleString()} · Non-fraud: {trainResult.non_fraud_count?.toLocaleString()}
            </p>
            {trainResult.preview?.length > 0 && (
              <>
                <h3 style={{ marginTop: '1.5rem' }}>Preview (first 100 rows) with Fraud Prediction</h3>
                <div className="table-wrap" style={{ marginTop: '0.5rem' }}>
                  <table>
                    <thead>
                      <tr>
                        {Object.keys(trainResult.preview[0]).map((c) => (
                          <th key={c}>{c}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {trainResult.preview.map((row, i) => (
                        <tr key={i}>
                          {Object.keys(trainResult.preview[0]).map((col) => (
                            <td key={col}>{String(row[col] ?? '')}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
