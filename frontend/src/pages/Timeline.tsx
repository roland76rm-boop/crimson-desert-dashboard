import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { formatSilver } from '../lib/utils'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { Panel } from '../components/Panel'
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts'

const tooltipStyle = {
  contentStyle: { background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 0, fontSize: 12 },
  labelStyle: { color: '#a0a0b8' },
}
const axisTick = { fill: '#6a6a85', fontSize: 11 }

export default function Timeline() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['timeline'], queryFn: () => api.timeline(30) })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorMessage message="Timeline konnte nicht geladen werden." />

  const points = data ?? []
  if (points.length === 0) {
    return (
      <div className="gh-card gh-eyebrow" style={{ textAlign: 'center', padding: '48px 16px' }}>
        Noch keine Daten für die Timeline
      </div>
    )
  }

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
    <div className="flex flex-col gap-5">
      <Panel eyebrow="Verlauf" title="Level über Zeit">
        <div className="p-4">
          <ResponsiveContainer width="100%" height={210}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="date" tick={axisTick} />
              <YAxis tick={axisTick} />
              <Tooltip {...tooltipStyle} itemStyle={{ color: '#f59e0b' }} />
              <Line type="monotone" dataKey="level" stroke="#f59e0b" strokeWidth={2} dot={{ fill: '#f59e0b', r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <Panel eyebrow="Verlauf" title="Silber über Zeit">
        <div className="p-4">
          <ResponsiveContainer width="100%" height={210}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="date" tick={axisTick} />
              <YAxis tick={axisTick} tickFormatter={v => formatSilver(v)} />
              <Tooltip {...tooltipStyle} itemStyle={{ color: '#f59e0b' }} formatter={(v: unknown) => formatSilver(v as number)} />
              <Area type="monotone" dataKey="silver" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.15} strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Panel eyebrow="Verlauf" title="Spielzeit (Stunden)">
          <div className="p-4">
            <ResponsiveContainer width="100%" height={190}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="date" tick={axisTick} />
                <YAxis tick={axisTick} />
                <Tooltip {...tooltipStyle} itemStyle={{ color: '#f43f5e' }} />
                <Bar dataKey="playtime_h" fill="#f43f5e" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel eyebrow="Verlauf" title="Quests abgeschlossen">
          <div className="p-4">
            <ResponsiveContainer width="100%" height={190}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="date" tick={axisTick} />
                <YAxis tick={axisTick} allowDecimals={false} />
                <Tooltip {...tooltipStyle} itemStyle={{ color: '#4ade80' }} />
                <Bar dataKey="quests" fill="#4ade80" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>
    </div>
  )
}
