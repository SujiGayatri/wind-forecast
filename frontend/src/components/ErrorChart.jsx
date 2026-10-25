import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts'

export default function ErrorChart({ data }) {
  const chartData = data.filter(x => x.error != null).map(x => ({ ...x, label: new Date(x.startTime).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }) }))
  return (
    <div className="chart-wrap">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 10, right: 16, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="label" minTickGap={20} stroke="#64748b" />
          <YAxis stroke="#64748b" tickFormatter={v => `${Math.round(v / 1000)}k`} />
          <Tooltip formatter={(v) => [`${Number(v).toLocaleString()} MW`, 'Error']} />
          <ReferenceLine y={0} stroke="#94a3b8" />
          <Bar dataKey="error" name="Forecast error (Actual − Forecast)" fill="#f59e0b" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
