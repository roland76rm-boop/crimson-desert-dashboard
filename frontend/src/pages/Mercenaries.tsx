import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const typeLabels: Record<string, string> = {
  companion: 'Begleiter',
  pet: 'Tier',
  mount: 'Reittier',
}

const typeIcons: Record<string, string> = {
  companion: '\u2694',
  pet: '\uD83D\uDC3E',
  mount: '\uD83D\uDC0E',
}

export default function Mercenaries() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['mercenaries'], queryFn: api.mercenaries })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorMessage message="Söldner konnten nicht geladen werden." />

  const mercs = data ?? []

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-gold">Söldner & Begleiter</h2>
      {mercs.length === 0 ? (
        <p className="text-slate-500">Noch keine Söldner oder Begleiter.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {mercs.map((m, i) => (
            <div key={`${m.merc_key}-${i}`} className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{typeIcons[m.type] ?? '\u2726'}</span>
                <div>
                  <p className="font-medium text-slate-200">{m.custom_name ?? m.name}</p>
                  {m.custom_name && <p className="text-xs text-slate-500">({m.name})</p>}
                  <p className="text-xs text-slate-400 mt-0.5">{typeLabels[m.type] ?? m.type}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
