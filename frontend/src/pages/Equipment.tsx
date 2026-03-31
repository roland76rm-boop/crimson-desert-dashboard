import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const slotLabels: Record<string, string> = {
  weapon: 'Waffe',
  helm: 'Helm',
  chest: 'Rüstung',
  legs: 'Beine',
  boots: 'Stiefel',
  gloves: 'Handschuhe',
  offhand: 'Nebenhand',
  ring: 'Ring',
  amulet: 'Amulett',
}

function Bar({ value, max = 100, color }: { value: number; max?: number; color: string }) {
  const pct = Math.min(100, (value / max) * 100)
  return (
    <div className="w-full bg-slate-700 rounded-full h-2">
      <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
    </div>
  )
}

export default function Equipment() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['equipment'], queryFn: api.equipment })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorMessage message="Equipment konnte nicht geladen werden." />

  const items = data ?? []

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {items.map((eq, i) => (
        <div key={`${eq.item_key}-${i}`} className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-wider">{slotLabels[eq.slot_type] ?? eq.slot_type}</p>
              <p className="font-medium text-gold">{eq.item_name ?? eq.item_key}</p>
            </div>
            <span className="bg-crimson/20 text-crimson px-2 py-0.5 rounded text-xs font-bold">
              +{eq.enchant_level}
            </span>
          </div>
          <div className="space-y-2">
            <div>
              <div className="flex justify-between text-xs mb-0.5">
                <span className="text-slate-400">Haltbarkeit</span>
                <span className="text-slate-300">{eq.endurance}%</span>
              </div>
              <Bar value={eq.endurance} color="bg-green-500" />
            </div>
            <div>
              <div className="flex justify-between text-xs mb-0.5">
                <span className="text-slate-400">Schärfe</span>
                <span className="text-slate-300">{eq.sharpness}%</span>
              </div>
              <Bar value={eq.sharpness} color="bg-blue-400" />
            </div>
          </div>
        </div>
      ))}
      {items.length === 0 && (
        <p className="text-slate-500 col-span-full text-center py-8">Kein Equipment vorhanden.</p>
      )}
    </div>
  )
}
