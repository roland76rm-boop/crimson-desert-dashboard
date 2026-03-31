import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { formatDate } from '../lib/utils'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function Quests() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['quests'], queryFn: api.quests })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorMessage message="Quests konnten nicht geladen werden." />

  const quests = data ?? []
  const active = quests.filter(q => q.status === 'active')
  const completed = quests.filter(q => q.status === 'completed')
  const failed = quests.filter(q => q.status === 'failed')

  const statusBadge: Record<string, string> = {
    active: 'bg-gold/20 text-gold',
    completed: 'bg-green-500/20 text-green-400',
    failed: 'bg-crimson/20 text-crimson',
  }

  const total = quests.length
  const pct = total > 0 ? Math.round((completed.length / total) * 100) : 0

  return (
    <div className="space-y-6">
      {/* Progress bar */}
      <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-slate-400">Quest-Fortschritt</span>
          <span className="text-gold font-medium">{completed.length}/{total} ({pct}%)</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-3">
          <div className="h-3 rounded-full bg-gold" style={{ width: `${pct}%` }} />
        </div>
      </div>

      {/* Sections */}
      {[
        { title: 'Aktive Quests', items: active, emptyMsg: 'Keine aktiven Quests.' },
        { title: 'Abgeschlossen', items: completed, emptyMsg: 'Noch keine Quests abgeschlossen.' },
        ...(failed.length > 0 ? [{ title: 'Fehlgeschlagen', items: failed, emptyMsg: '' }] : []),
      ].map(section => (
        <div key={section.title}>
          <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
            {section.title} ({section.items.length})
          </h3>
          {section.items.length === 0 ? (
            <p className="text-slate-600 text-sm">{section.emptyMsg}</p>
          ) : (
            <div className="space-y-2">
              {section.items.map((q, i) => (
                <div key={`${q.quest_key}-${i}`} className="bg-slate-800 rounded-lg px-4 py-3 border border-slate-700 flex items-center justify-between">
                  <div>
                    <p className="font-medium">{q.quest_name ?? q.quest_key}</p>
                    {q.completed_at && <p className="text-xs text-slate-500 mt-0.5">Abgeschlossen: {formatDate(q.completed_at)}</p>}
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusBadge[q.status] ?? 'bg-slate-700 text-slate-400'}`}>
                    {q.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
