import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { formatDate } from '../lib/utils'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { Panel } from '../components/Panel'

const STATUS_COLOR: Record<string, string> = {
  active: 'var(--accent)',
  completed: 'var(--ok)',
  failed: 'var(--bad)',
}

export default function Quests() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['quests'], queryFn: api.quests })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorMessage message="Quests konnten nicht geladen werden." />

  const quests = data ?? []
  const active = quests.filter(q => q.status === 'active')
  const completed = quests.filter(q => q.status === 'completed')
  const failed = quests.filter(q => q.status === 'failed')

  const total = quests.length
  const pct = total > 0 ? Math.round((completed.length / total) * 100) : 0

  return (
    <div className="flex flex-col gap-5">
      {/* Fortschritt */}
      <section className="gh-card" style={{ padding: 16 }}>
        <div className="flex justify-between items-baseline mb-2">
          <span className="gh-eyebrow">Quest-Fortschritt</span>
          <span className="gh-mono" style={{ fontSize: 12, color: 'var(--accent)', fontWeight: 600 }}>
            {completed.length}/{total} · {pct}%
          </span>
        </div>
        <div style={{ height: 6, background: 'rgba(0,0,0,0.4)' }}>
          <div style={{ height: '100%', width: `${pct}%`, background: 'var(--accent)' }} />
        </div>
      </section>

      {[
        { title: 'Aktive Quests', items: active, emptyMsg: 'Keine aktiven Quests.' },
        { title: 'Abgeschlossen', items: completed, emptyMsg: 'Noch keine Quests abgeschlossen.' },
        ...(failed.length > 0 ? [{ title: 'Fehlgeschlagen', items: failed, emptyMsg: '' }] : []),
      ].map(section => (
        <Panel key={section.title} eyebrow="Quests" title={`${section.title} · ${section.items.length}`}>
          {section.items.length === 0 ? (
            <p style={{ padding: '14px 16px', fontSize: 12, color: 'var(--fg-mute)' }}>{section.emptyMsg}</p>
          ) : (
            <div>
              {section.items.map((q, i) => (
                <div
                  key={`${q.quest_key}-${i}`}
                  className="flex items-center justify-between px-4 py-3"
                  style={{
                    borderTop: i > 0 ? '1px solid var(--hairline)' : 'none',
                    borderLeft: `2px solid ${STATUS_COLOR[q.status] ?? 'var(--border-2)'}`,
                  }}
                >
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: 12.5, color: '#fff', fontWeight: 500 }}>{q.quest_name ?? q.quest_key}</div>
                    {q.completed_at && (
                      <div className="gh-mono" style={{ fontSize: 10, color: 'var(--fg-faint)', marginTop: 2 }}>
                        Abgeschlossen: {formatDate(q.completed_at)}
                      </div>
                    )}
                  </div>
                  <span className="gh-mono shrink-0" style={{
                    fontSize: 9.5, padding: '2px 8px', letterSpacing: '0.08em', textTransform: 'uppercase',
                    color: STATUS_COLOR[q.status] ?? 'var(--fg-mute)',
                    border: `1px solid ${STATUS_COLOR[q.status] ?? 'var(--border-2)'}55`,
                    background: `${STATUS_COLOR[q.status] ?? 'transparent'}14`,
                  }}>
                    {q.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </Panel>
      ))}
    </div>
  )
}
