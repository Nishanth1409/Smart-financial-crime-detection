import { useState, useEffect } from 'react'
import { getPersonFraud, getPersons } from '../api'

export default function PersonFraud() {
  const [personId, setPersonId] = useState('')
  const [limit, setLimit] = useState(100)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [persons, setPersons] = useState([])
  const [personsLoading, setPersonsLoading] = useState(true)

  useEffect(() => {
    getPersons(500)
      .then((res) => setPersons(res.persons || []))
      .catch(() => setPersons([]))
      .finally(() => setPersonsLoading(false))
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!personId.trim()) return
    setLoading(true)
    setError(null)
    setData(null)
    try {
      const res = await getPersonFraud(personId.trim(), limit)
      setData(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const selectedPersonName = persons.find((p) => p.id === personId)?.name || personId || null

  return (
    <div className="page-content">
      <h1 className="page-title">Person Fraud Detection</h1>
      <p className="page-subtitle">
        Select or type a person/account from the CSV to see fraud risk. Each transaction is scored with a Logistic Regression (linear) model.
      </p>

      <form onSubmit={handleSubmit} className="card" style={{ maxWidth: 720 }}>
        <div className="form-grid" style={{ gridTemplateColumns: '1fr 1fr auto auto' }}>
          <div className="form-group">
            <label>Person / Account (loaded from CSV)</label>
            <select
              value={personId}
              onChange={(e) => { setPersonId(e.target.value); setError(null); setData(null); }}
              disabled={personsLoading}
            >
              <option value="">Select or type below…</option>
              {persons.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.id})
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Or type Account ID (nameOrig)</label>
            <input
              type="text"
              value={personId}
              onChange={(e) => { setPersonId(e.target.value); setError(null); setData(null); }}
              placeholder="e.g. C1234567890"
              list="person-list"
            />
            <datalist id="person-list">
              {persons.slice(0, 100).map((p) => (
                <option key={p.id} value={p.id} label={p.name} />
              ))}
            </datalist>
          </div>
          <div className="form-group">
            <label>Max transactions</label>
            <select value={limit} onChange={(e) => setLimit(Number(e.target.value))}>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
              <option value={500}>500</option>
            </select>
          </div>
          <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button type="submit" className="btn btn-primary" disabled={loading || !personId.trim()}>
              {loading ? 'Loading…' : 'Check fraud risk'}
            </button>
          </div>
        </div>
      </form>

      {error && <div className="error" style={{ marginTop: '1rem' }}>{error}</div>}

      {data && (
        <>
          <div className="card" style={{ marginTop: '1.5rem' }}>
            <h3>Person</h3>
            <p style={{ margin: 0 }}>
              <strong>Name / ID:</strong> {data.person_name || data.person_id}
              {selectedPersonName && selectedPersonName !== data.person_id && ` (${data.person_id})`}
            </p>
          </div>
          <div className="metrics" style={{ marginTop: '1rem' }}>
            <div className="metric">
              <div className="value">{data.transaction_count}</div>
              <div className="label">Transactions found</div>
            </div>
            <div className="metric">
              <div className="value">{data.max_fraud_risk_pct}%</div>
              <div className="label">Max fraud risk (worst tx)</div>
            </div>
            <div className="metric">
              <div className="value">{data.mean_fraud_risk_pct}%</div>
              <div className="label">Mean fraud risk</div>
            </div>
            <div className="metric">
              <div className="value" style={{ textTransform: 'capitalize' }}>{data.overall_risk_level}</div>
              <div className="label">Overall person risk</div>
            </div>
          </div>

          <div className="card" style={{ marginTop: '1rem' }}>
            <h3>Model: {data.model_info}</h3>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Step</th>
                    <th>Type</th>
                    <th>Amount</th>
                    <th>Fraud risk %</th>
                    <th>Risk</th>
                    <th>Predicted</th>
                  </tr>
                </thead>
                <tbody>
                  {data.transactions.map((tx, i) => (
                    <tr key={i}>
                      <td>{tx.step}</td>
                      <td>{tx.type}</td>
                      <td>{Number(tx.amount).toLocaleString()}</td>
                      <td>{tx.fraud_risk_pct}%</td>
                      <td>
                        <span className={`risk-badge ${tx.risk_level}`}>{tx.risk_level}</span>
                      </td>
                      <td>{tx.fraud_prediction === 1 ? '⚠ Fraud' : 'OK'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
