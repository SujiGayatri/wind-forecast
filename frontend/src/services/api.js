const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function getAnalysis() {
  const response = await fetch(`${API_URL}/api/analysis`)
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || 'Failed to load analysis')
  }
  return response.json()
}
