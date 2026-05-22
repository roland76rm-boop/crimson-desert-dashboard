import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { formatPlaytime, formatSilver, timeAgo } from '../lib/utils'
import StatCard from '../components/StatCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { Panel } from '../components/Panel'
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
    <div className="flex flex-col gap-5">
      {/* Charakter-Banner */}
      <section className="gh-card gh-card-strip" style={{ padding: 20, overflow: 'hidden' }}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5">
          <div style={{
            width: 60, height: 60, flexShrink: 0, display: 'grid', placeItems: 'center', fontSize: 26,
            background: 'rgb(var(--accent-glow) / 0.1)', border: '1px solid rgb(var(--accent-glow) / 0.4)',
          }}>
            &#9876;
          </div>
          <div className="flex-1" style={{ minWidth: 0 }}>
            <div className="gh-eyebrow-accent">Aktiver Charakter</div>
            <h2 className="gh-display" style={{ fontSize: 24, fontWeight: 700, color: '#fff', margin: '4px 0 0' }}>
              {c.name ?? 'Unbekannt'}
            </h2>
            <div className="gh-mono" style={{ fontSize: 11, color: 'var(--fg-mute)', marginTop: 4 }}>
              Level {c.level} · {formatPlaytime(c.playtime_seconds)} Spielzeit · Snapshot {timeAgo(c.uploaded_at)}
            </div>
          </div>
          <Link to="/upload" className="gh-btn gh-btn-primary shrink-0" style={{ textDecoration: 'none' }}>
            Save hochladen
          </Link>
        </div>
      </section>

      {/* Kennzahlen */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Level" value={c.level ?? '—'} accent="gold" />
        <StatCard label="Silber" value={formatSilver(c.currency_silver)} accent="gold" />
        <StatCard label="Items" value={inv.data?.length ?? '—'} />
        <StatCard label="Quests" value={`${completedQuests}/${totalQuests}`} sub="abgeschlossen" accent="crimson" />
      </div>

      {/* Stats */}
      {c.stats && Object.keys(c.stats).length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(c.stats).map(([key, val]) => (
            <StatCard key={key} label={key} value={val} />
          ))}
        </div>
      )}

      {/* Level-Chart */}
      {chartData.length > 1 && (
        <Panel eyebrow="Verlauf" title="Level-Fortschritt">
          <div className="p-4">
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="date" tick={{ fill: '#6a6a85', fontSize: 11 }} />
                <YAxis tick={{ fill: '#6a6a85', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 0, fontSize: 12 }}
                  labelStyle={{ color: '#a0a0b8' }}
                  itemStyle={{ color: '#f59e0b' }}
                />
                <Line type="monotone" dataKey="level" stroke="#f59e0b" strokeWidth={2} dot={{ fill: '#f59e0b', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      )}
    </div>
  )
}
