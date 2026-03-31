import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { formatSilver } from '../lib/utils'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts'

const tooltipStyle = {
  contentStyle: { backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: 8 },
  labelStyle: { color: '#94A3B8' },
}

export default function Timeline() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['timeline'], queryFn: () => api.timeline(30) })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorMessage message="Timeline konnte nicht geladen werden." />

  const points = data ?? []
  if (points.length === 0) return <p className="text-slate-500">Noch keine Daten für die Timeline.</p>

  const chartData = points.map(p => {
    const d = new Date(p.uploaded_at)
    return {
      date: d.toLocaleDateString('de-AT', { day: '2-digit', month: '2-digit' }),
      level: p.character_level,
      silver: p.currency_silver,
      playtime_h: p.playtime_seconds ? +(p.playtime_seconds / 3600).toFixed(1) : 0,
      items: p.inventory_count,
      quests: p.quests_completed,
    }
  })

  return (
    <div className="space-y-6">
      {/* Level */}
      <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-400 mb-4">Level über Zeit</h3>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="date" tick={{ fill: '#94A3B8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#94A3B8', fontSize: 12 }} />
            <Tooltip {...tooltipStyle} />
            <Line type="monotone" dataKey="level" stroke="#D4AF37" strokeWidth={2} dot={{ fill: '#D4AF37', r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Silver */}
      <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-400 mb-4">Silber über Zeit</h3>
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="date" tick={{ fill: '#94A3B8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#94A3B8', fontSize: 12 }} tickFormatter={v => formatSilver(v)} />
            <Tooltip {...tooltipStyle} formatter={(v: unknown) => formatSilver(v as number)} />
            <Area type="monotone" dataKey="silver" stroke="#D4AF37" fill="#D4AF37" fillOpacity={0.15} strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Playtime */}
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-400 mb-4">Spielzeit (Stunden)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" tick={{ fill: '#94A3B8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94A3B8', fontSize: 11 }} />
              <Tooltip {...tooltipStyle} />
              <Bar dataKey="playtime_h" fill="#DC2626" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Quests completed */}
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-400 mb-4">Quests abgeschlossen</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" tick={{ fill: '#94A3B8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94A3B8', fontSize: 11 }} allowDecimals={false} />
              <Tooltip {...tooltipStyle} />
              <Bar dataKey="quests" fill="#22C55E" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
