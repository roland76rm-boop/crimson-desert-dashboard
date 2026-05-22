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

function Bar({ label, value, color }: { label: string; value: number; color: string }) {
  const pct = Math.min(100, value)
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="gh-eyebrow" style={{ fontSize: 9 }}>{label}</span>
        <span className="gh-mono" style={{ fontSize: 10.5, color: 'var(--fg-dim)' }}>{value}%</span>
      </div>
      <div style={{ height: 5, background: 'rgba(0,0,0,0.4)' }}>
        <div style={{ height: '100%', width: `${pct}%`, background: color }} />
      </div>
    </div>
  )
}

export default function Equipment() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['equipment'], queryFn: api.equipment })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorMessage message="Equipment konnte nicht geladen werden." />

  const items = data ?? []

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      {items.map((eq, i) => (
        <div key={`${eq.item_key}-${i}`} className="gh-card" style={{ padding: 15, borderLeft: '2px solid var(--accent)' }}>
          <div className="flex items-center justify-between mb-3">
            <div style={{ minWidth: 0 }}>
              <div className="gh-eyebrow" style={{ fontSize: 9 }}>{slotLabels[eq.slot_type] ?? eq.slot_type}</div>
              <div className="gh-display" style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent)', marginTop: 3 }}>
                {eq.item_name ?? eq.item_key}
              </div>
            </div>
            <span className="gh-mono shrink-0" style={{
              fontSize: 11, padding: '2px 8px', fontWeight: 700, color: 'var(--bad)',
              border: '1px solid rgba(244,63,94,0.4)', background: 'rgba(244,63,94,0.12)',
            }}>
              +{eq.enchant_level}
            </span>
          </div>
          <div className="flex flex-col gap-2.5">
            <Bar label="Haltbarkeit" value={eq.endurance} color="var(--ok)" />
            <Bar label="Schärfe" value={eq.sharpness} color="var(--info)" />
          </div>
        </div>
      ))}
      {items.length === 0 && (
        <div className="gh-card gh-eyebrow col-span-full" style={{ textAlign: 'center', padding: '36px 16px' }}>
          Kein Equipment vorhanden
        </div>
      )}
    </div>
  )
}
