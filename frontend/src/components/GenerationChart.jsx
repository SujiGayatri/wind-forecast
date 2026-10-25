import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

function formatTick(value) {
  const d = new Date(value)
  return `${String(d.getUTCHours()).padStart(2, '0')}:${String(d.getUTCMinutes()).padStart(2, '0')}`
}

export default function GenerationChart({ data }) {
  const chartData = data.filter(x => x.actualGeneration != null).map(x => ({ ...x, label: formatTick(x.startTime) }))
  return (
    <div className="chart-wrap">
      <ResponsiveContainer width="100%" height={360}>
        <LineChart data={chartData} margin={{ top: 10, right: 16, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="label" minTickGap={30} stroke="#64748b" />
          <YAxis stroke="#64748b" tickFormatter={v => `${Math.round(v / 1000)}k`} />
          <Tooltip formatter={(v) => [`${Number(v).toLocaleString()} MW`]} labelFormatter={(_, p) => p?.[0]?.payload?.startTime || ''} />
          <Legend />
          <Line type="monotone" dataKey="generation" name="Forecast" stroke="#0f766e" strokeWidth={2.5} dot={false} />
          <Line type="monotone" dataKey="actualGeneration" name="Actual" stroke="#334155" strokeWidth={2.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
