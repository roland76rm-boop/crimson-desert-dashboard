import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { Panel } from '../components/Panel'

const typeLabels: Record<string, string> = {
  companion: 'Begleiter',
  pet: 'Tier',
  mount: 'Reittier',
}

export default function Mercenaries() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['mercenaries'], queryFn: api.mercenaries })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorMessage message="Söldner konnten nicht geladen werden." />

  const mercs = data ?? []

  return (
    <Panel eyebrow="Gefolge" title={`Söldner & Begleiter · ${mercs.length}`}>
      {mercs.length === 0 ? (
        <p style={{ padding: '14px 16px', fontSize: 12, color: 'var(--fg-mute)' }}>Noch keine Söldner oder Begleiter.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 p-4">
          {mercs.map((m, i) => (
            <div key={`${m.merc_key}-${i}`} style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid var(--hairline)', borderLeft: '2px solid var(--accent)', padding: 13 }}>
              <div className="gh-eyebrow" style={{ fontSize: 8.5 }}>{typeLabels[m.type] ?? m.type}</div>
              <div className="gh-display" style={{ fontSize: 13, fontWeight: 700, color: '#fff', marginTop: 4 }}>
                {m.custom_name ?? m.name}
              </div>
              {m.custom_name && (
                <div className="gh-mono" style={{ fontSize: 10, color: 'var(--fg-mute)', marginTop: 2 }}>({m.name})</div>
              )}
            </div>
          ))}
        </div>
      )}
    </Panel>
  )
}
