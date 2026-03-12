import { useState } from 'react'
import { predictTransaction } from '../api'

const TYPES = ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT']

export default function Predict() {
  const [form, setForm] = useState({
    type: 'PAYMENT',
    amount: 0,
    oldbalanceOrg: 0,
    newbalanceOrig: 0,
    oldbalanceDest: 0,
    newbalanceDest: 0,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: name === 'type' ? value : Number(value) || 0 }))
    setResult(null)
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await predictTransaction(form)
      setResult(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-content">
      <h1 className="page-title">Transaction Fraud Detection</h1>
      <p className="page-subtitle">Enter transaction details to get a fraud risk score.</p>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label>Transaction Type</label>
            <select name="type" value={form.type} onChange={handleChange}>
              {TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Amount</label>
            <input type="number" name="amount" value={form.amount || ''} onChange={handleChange} min={0} step="any" />
          </div>
          <div className="form-group">
            <label>Old Balance Sender</label>
            <input type="number" name="oldbalanceOrg" value={form.oldbalanceOrg || ''} onChange={handleChange} min={0} step="any" />
          </div>
          <div className="form-group">
            <label>New Balance Sender</label>
            <input type="number" name="newbalanceOrig" value={form.newbalanceOrig || ''} onChange={handleChange} min={0} step="any" />
          </div>
          <div className="form-group">
            <label>Old Balance Receiver</label>
            <input type="number" name="oldbalanceDest" value={form.oldbalanceDest || ''} onChange={handleChange} min={0} step="any" />
          </div>
          <div className="form-group">
            <label>New Balance Receiver</label>
            <input type="number" name="newbalanceDest" value={form.newbalanceDest || ''} onChange={handleChange} min={0} step="any" />
          </div>
        </div>
        <div style={{ marginTop: '1rem' }}>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Predicting…' : 'Predict Fraud'}
          </button>
        </div>
      </form>

      {error && <div className="error" style={{ marginTop: '1rem' }}>{error}</div>}

      {result && (
        <div className={`result-box ${result.risk_level}`} style={{ marginTop: '1.5rem' }}>
          <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>
            Fraud Risk Score: {result.fraud_risk_pct}%
          </div>
          <div className="progress-bar" style={{ marginTop: '0.5rem' }}>
            <div
              className="fill"
              style={{
                width: `${result.fraud_probability * 100}%`,
                background: result.risk_level === 'high' ? 'var(--danger)' : result.risk_level === 'medium' ? 'var(--warn)' : 'var(--success)',
              }}
            />
          </div>
          <div style={{ marginTop: '0.5rem' }}>
            {result.risk_level === 'low' && '🟢 Low Risk Transaction'}
            {result.risk_level === 'medium' && '🟡 Medium Risk Transaction'}
            {result.risk_level === 'high' && '🔴 High Fraud Risk'}
          </div>
        </div>
      )}
    </div>
  )
}
