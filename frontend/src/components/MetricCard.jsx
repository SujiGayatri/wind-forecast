export default function MetricCard({ label, value, suffix = '' }) {
  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <strong>{value ?? '—'}{value != null ? suffix : ''}</strong>
    </div>
  )
}
