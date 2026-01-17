import React, { useEffect, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js'
import 'chartjs-adapter-date-fns'
import { Line, Bar } from 'react-chartjs-2'

import {
  fetchOverview,
  fetchTimeline,
  fetchTopIPs,
  fetchCredentials,
  fetchAlerts,
} from './api'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  TimeScale,
)

const REFRESH_MS = 8000

function OverviewCards({ data }) {
  const cards = [
    { label: 'Total Events', value: data?.total_events ?? 0 },
    { label: 'Unique IPs', value: data?.unique_ips ?? 0 },
    { label: 'High-Risk IPs', value: data?.high_risk_ips ?? 0 },
    { label: 'Open Alerts', value: data?.open_alerts ?? 0 },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {cards.map((c) => (
        <div
          key={c.label}
          className="rounded-xl bg-slate-900/70 border border-slate-800 px-4 py-3 shadow-sm"
        >
          <div className="text-xs uppercase tracking-wide text-slate-400">
            {c.label}
          </div>
          <div className="mt-2 text-2xl font-semibold text-emerald-400">
            {c.value}
          </div>
        </div>
      ))}
    </div>
  )
}

function AttackTimeline({ data }) {
  const points = data?.points ?? []
  const labels = points.map((p) => p.bucket_start)
  const counts = points.map((p) => p.count)

  const chartData = {
    labels,
    datasets: [
      {
        label: 'SSH Attempts',
        data: counts,
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
      },
    ],
  }

  const options = {
    responsive: true,
    plugins: {
      legend: { labels: { color: '#e5e7eb' } },
    },
    scales: {
      x: {
        type: 'time',
        ticks: { color: '#9ca3af' },
        grid: { color: 'rgba(55,65,81,0.5)' },
      },
      y: {
        ticks: { color: '#9ca3af' },
        grid: { color: 'rgba(55,65,81,0.5)' },
      },
    },
  }

  return (
    <div className="rounded-xl bg-slate-900/70 border border-slate-800 p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-slate-200">Attack Timeline (last 6h)</h2>
      </div>
      <Line data={chartData} options={options} height={80} />
    </div>
  )
}

function TopIPs({ data }) {
  const ips = data?.ips ?? []

  const chartData = {
    labels: ips.map((ip) => ip.ip),
    datasets: [
      {
        label: 'Events',
        data: ips.map((ip) => ip.events),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
      },
    ],
  }

  const options = {
    responsive: true,
    plugins: {
      legend: { labels: { color: '#e5e7eb' } },
    },
    scales: {
      x: { ticks: { color: '#9ca3af' } },
      y: { ticks: { color: '#9ca3af' } },
    },
  }

  return (
    <div className="rounded-xl bg-slate-900/70 border border-slate-800 p-4 h-full flex flex-col">
      <h2 className="text-sm font-semibold text-slate-200 mb-3">Top Attacking IPs</h2>
      <Bar data={chartData} options={options} height={80} />
      <div className="mt-4 text-xs text-slate-400">
        <p>Risk scores:</p>
        <ul className="mt-1 space-y-1">
          {ips.map((ip) => (
            <li key={ip.ip} className="flex justify-between">
              <span className="font-mono">{ip.ip}</span>
              <span className="text-emerald-400">score {ip.score.toFixed(1)}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

function CredentialHeatmap({ data }) {
  const creds = data?.credentials ?? []

  return (
    <div className="rounded-xl bg-slate-900/70 border border-slate-800 p-4 h-full">
      <h2 className="text-sm font-semibold text-slate-200 mb-3">Credential Heatmap</h2>
      <div className="text-xs text-slate-400 mb-2">
        Most targeted usernames (size = attempts).
      </div>
      <div className="flex flex-wrap gap-2">
        {creds.map((c) => (
          <div
            key={c.username}
            className="rounded-full px-3 py-1 bg-emerald-500/10 border border-emerald-500/40 text-emerald-300"
            style={{ fontSize: 0.7 + Math.min(c.attempts / 20, 1.3) + 'rem' }}
          >
            <span className="font-mono">{c.username || '(blank)'}</span>
            <span className="ml-1 text-emerald-200/70">×{c.attempts}</span>
          </div>
        ))}
        {creds.length === 0 && (
          <div className="text-xs text-slate-500">No credential data yet.</div>
        )}
      </div>
    </div>
  )
}

function RiskSeverity({ overview }) {
  const highRisk = overview?.high_risk_ips ?? 0

  const level =
    highRisk >= 5 ? 'critical' : highRisk >= 3 ? 'high' : highRisk >= 1 ? 'elevated' : 'low'

  const colorMap = {
    low: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/60',
    elevated: 'bg-amber-500/20 text-amber-300 border-amber-500/60',
    high: 'bg-orange-500/20 text-orange-300 border-orange-500/60',
    critical: 'bg-red-500/20 text-red-300 border-red-500/60',
  }

  return (
    <div className={`rounded-xl border px-4 py-3 ${colorMap[level]}`}>
      <div className="text-xs uppercase tracking-wide">Risk level</div>
      <div className="mt-1 text-xl font-semibold">{level.toUpperCase()}</div>
      <div className="mt-1 text-xs opacity-80">
        {highRisk} high-risk IPs currently detected.
      </div>
    </div>
  )
}

function AlertsPanel({ data }) {
  const alerts = data?.alerts ?? []

  return (
    <div className="rounded-xl bg-slate-900/70 border border-slate-800 p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-slate-200">Alerts</h2>
        <span className="text-xs text-slate-500">Newest first</span>
      </div>
      <div className="space-y-2 overflow-y-auto max-h-80 pr-1">
        {alerts.map((a) => (
          <div
            key={a.id}
            className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs"
          >
            <div className="flex justify-between">
              <span className="font-semibold text-red-300">{a.title}</span>
              <span className="font-mono text-red-200/80">{a.ip}</span>
            </div>
            <div className="mt-1 text-red-100/90 text-[11px]">{a.description}</div>
            <div className="mt-1 text-[10px] text-red-200/70">
              {new Date(a.created_at).toLocaleString()} · severity {a.severity}
            </div>
          </div>
        ))}
        {alerts.length === 0 && (
          <div className="text-xs text-slate-500">No alerts yet. System is quiet.</div>
        )}
      </div>
    </div>
  )
}

export default function App() {
  const [overview, setOverview] = useState(null)
  const [timeline, setTimeline] = useState(null)
  const [topIPs, setTopIPs] = useState(null)
  const [creds, setCreds] = useState(null)
  const [alerts, setAlerts] = useState(null)

  useEffect(() => {
    let cancelled = false

    async function loadAll() {
      try {
        const [ov, tl, ti, cr, al] = await Promise.all([
          fetchOverview(),
          fetchTimeline(),
          fetchTopIPs(),
          fetchCredentials(),
          fetchAlerts(),
        ])
        if (!cancelled) {
          setOverview(ov)
          setTimeline(tl)
          setTopIPs(ti)
          setCreds(cr)
          setAlerts(al)
        }
      } catch (e) {
        console.error('Failed to load data', e)
      }
    }

    loadAll()
    const id = setInterval(loadAll, REFRESH_MS)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-emerald-500/20 border border-emerald-500/60 flex items-center justify-center text-emerald-300 font-bold text-sm">
              HS
            </div>
            <div>
              <div className="text-sm font-semibold tracking-wide">HoneyShield</div>
              <div className="text-[11px] text-slate-500">
                SSH honeypot · mini SIEM dashboard
              </div>
            </div>
          </div>
          <div className="text-[11px] text-slate-500">
            Live polling every {REFRESH_MS / 1000}s
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-4 md:py-6">
        <OverviewCards data={overview} />

        <div className="grid md:grid-cols-3 gap-4 mb-4">
          <div className="md:col-span-2">
            <AttackTimeline data={timeline} />
          </div>
          <div className="flex flex-col gap-3">
            <RiskSeverity overview={overview} />
            <CredentialHeatmap data={creds} />
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <AlertsPanel data={alerts} />
          </div>
          <TopIPs data={topIPs} />
        </div>
      </main>
    </div>
  )
}
