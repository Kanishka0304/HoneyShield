import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

export async function fetchOverview() {
  const res = await axios.get(`${API_BASE}/stats/overview`)
  return res.data
}

export async function fetchTimeline() {
  const res = await axios.get(`${API_BASE}/stats/timeline`)
  return res.data
}

export async function fetchTopIPs() {
  const res = await axios.get(`${API_BASE}/stats/top-ips`)
  return res.data
}

export async function fetchCredentials() {
  const res = await axios.get(`${API_BASE}/stats/credentials`)
  return res.data
}

export async function fetchAlerts() {
  const res = await axios.get(`${API_BASE}/alerts`)
  return res.data
}
