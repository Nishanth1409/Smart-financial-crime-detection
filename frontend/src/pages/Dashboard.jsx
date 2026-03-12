import { useState, useEffect } from 'react'
import { getDashboardStats } from '../api'
import EChartsBar from '../components/EChartsBar'
import EChartsLine from '../components/EChartsLine'
import EChartsDailyWeekly from '../components/EChartsDailyWeekly'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getDashboardStats()
      .then(setStats)
      .catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="page-content"><div className="error">Failed to load dashboard: {error}</div></div>
  if (!stats) return <div className="page-content"><div className="loading">Loading dashboard…</div></div>

  return (
    <div className="page-content">
      <h1 className="page-title">Financial Fraud Monitoring</h1>
      <p className="page-subtitle">
        Fraud = detected/actual (≥50% risk). Not fraud = below 50% (normal).
      </p>

      <div className="metrics">
        <div className="metric">
          <div className="value">{stats.total_transactions.toLocaleString()}</div>
          <div className="label">Total Transactions</div>
        </div>
        <div className="metric">
          <div className="value">{stats.fraud_cases.toLocaleString()}</div>
          <div className="label">Fraud (≥50%)</div>
        </div>
        <div className="metric">
          <div className="value">{stats.fraud_rate_pct}%</div>
          <div className="label">Fraud Rate</div>
        </div>
        <div className="metric">
          <div className="value">{stats.normal_transactions.toLocaleString()}</div>
          <div className="label">Not Fraud (&lt;50%)</div>
        </div>
      </div>

      {/* Daily: Fraud vs Not fraud by day */}
      {stats.daily_fraud?.length > 0 && (
        <div className="card animate-delay-1" style={{ marginTop: '1.5rem' }}>
          <h3>Daily: Fraud (≥50%) vs Not Fraud (&lt;50%)</h3>
          <p>Per day (step): how much fraud detection vs not fraud.</p>
          <EChartsDailyWeekly data={stats.daily_fraud} unitLabel="Day" />
          <div style={{ marginTop: '1rem' }}>
            <DailyWeeklyTable data={stats.daily_fraud} unit="day" unitLabel="Day" />
          </div>
        </div>
      )}

      {/* Weekly: Fraud vs Not fraud by week */}
      {stats.weekly_fraud?.length > 0 && (
        <div className="card animate-delay-2" style={{ marginTop: '1rem' }}>
          <h3>Weekly: Fraud (≥50%) vs Not Fraud (&lt;50%)</h3>
          <p>Per week: how much fraud detection vs not fraud.</p>
          <EChartsDailyWeekly data={stats.weekly_fraud} unitLabel="Week" />
          <div style={{ marginTop: '1rem' }}>
            <DailyWeeklyTable data={stats.weekly_fraud} unit="week" unitLabel="Week" />
          </div>
        </div>
      )}

      <div className="charts-row" style={{ marginTop: '1.5rem' }}>
        <div className="card animate-delay-3">
          <h3>Fraud vs Normal (overall)</h3>
          <EChartsBar data={stats.fraud_vs_normal} labelKey="label" valueKey="count" />
        </div>
        <div className="card animate-delay-4">
          <h3>Transaction Types</h3>
          <EChartsBar data={stats.transaction_types} valueKey="count" labelKey="type" />
        </div>
      </div>

      <div className="charts-row">
        <div className="card">
          <h3>Transaction Amount (sample)</h3>
          <EChartsLine data={stats.amount_sample} />
        </div>
        <div className="card">
          <h3>Fraud by Transaction Type</h3>
          <EChartsBar data={stats.fraud_by_type} valueKey="fraud_count" labelKey="type" />
        </div>
      </div>
    </div>
  )
}

function DailyWeeklyTable({ data, unit, unitLabel }) {
  if (!data?.length) return <div className="loading">No data</div>
  const displayData = data.length > 30 ? data.slice(-30) : data
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>{unitLabel}</th>
            <th>Fraud (≥50%)</th>
            <th>Not fraud (&lt;50%)</th>
            <th>Total</th>
            <th>Fraud %</th>
          </tr>
        </thead>
        <tbody>
          {displayData.map((row, i) => (
            <tr key={i}>
              <td>{row[unit]}</td>
              <td>{row.fraud_count.toLocaleString()}</td>
              <td>{row.not_fraud_count.toLocaleString()}</td>
              <td>{row.total.toLocaleString()}</td>
              <td>{row.fraud_pct}%</td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > 30 && (
        <p className="page-subtitle" style={{ marginTop: '0.75rem', marginBottom: 0 }}>Showing last 30 {unitLabel}s (of {data.length})</p>
      )}
    </div>
  )
}

