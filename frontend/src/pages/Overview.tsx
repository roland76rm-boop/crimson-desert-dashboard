import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { formatPlaytime, formatSilver, timeAgo } from '../lib/utils'
import StatCard from '../components/StatCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function Overview() {
  const char = useQuery({ queryKey: ['character'], queryFn: api.character })
  const timeline = useQuery({ queryKey: ['timeline'], queryFn: () => api.timeline(30) })
  const inv = useQuery({ queryKey: ['inventory'], queryFn: api.inventory })
  const quests = useQuery({ queryKey: ['quests'], queryFn: api.quests })

  if (char.isLoading) return <LoadingSpinner />
  if (char.isError) return <ErrorMessage message="Keine Daten verfügbar. Ist das Backend erreichbar?" />

  const c = char.data!
  const completedQuests = quests.data?.filter(q => q.status === 'completed').length ?? 0
  const totalQuests = quests.data?.length ?? 0

  const chartData = timeline.data?.map(p => ({
    date: new Date(p.uploaded_at).toLocaleDateString('de-AT', { day: '2-digit', month: '2-digit' }),
    level: p.character_level,
  })) ?? []

  return (
    <div className="space-y-6">
      {/* Character card */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 flex flex-col sm:flex-row items-start sm:items-center gap-6">
        <div className="w-16 h-16 bg-crimson/20 rounded-full flex items-center justify-center text-3xl border-2 border-crimson/40">
          &#9876;
        </div>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gold">{c.name ?? 'Unbekannt'}</h2>
          <p className="text-slate-400 mt-1">Level {c.level} &middot; {formatPlaytime(c.playtime_seconds)} Spielzeit</p>
          <p className="text-slate-500 text-sm mt-1">Letzter Snapshot: {timeAgo(c.uploaded_at)}</p>
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Level" value={c.level ?? '—'} accent="gold" />
        <StatCard label="Silber" value={formatSilver(c.currency_silver)} accent="gold" />
        <StatCard label="Items" value={inv.data?.length ?? '—'} />
        <StatCard label="Quests" value={`${completedQuests}/${totalQuests}`} sub="abgeschlossen" accent="crimson" />
      </div>

      {/* Stats */}
      {c.stats && Object.keys(c.stats).length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(c.stats).map(([key, val]) => (
            <StatCard key={key} label={key.toUpperCase()} value={val} />
          ))}
        </div>
      )}

      {/* Level chart */}
      {chartData.length > 1 && (
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-400 mb-4">Level-Fortschritt</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" tick={{ fill: '#94A3B8', fontSize: 12 }} />
              <YAxis tick={{ fill: '#94A3B8', fontSize: 12 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: 8 }}
                labelStyle={{ color: '#94A3B8' }}
              />
              <Line type="monotone" dataKey="level" stroke="#D4AF37" strokeWidth={2} dot={{ fill: '#D4AF37', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
