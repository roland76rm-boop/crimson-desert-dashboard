import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { Panel } from '../components/Panel'

const CATEGORIES = ['Alle', 'Equipment', 'Material', 'Consumable', 'Quest', 'Misc']

const CAT_COLOR: Record<string, string> = {
  Equipment: 'var(--accent)',
  Material: 'var(--info)',
  Consumable: 'var(--ok)',
  Quest: 'var(--bad)',
  Misc: 'var(--fg-mute)',
}

export default function Inventory() {
  const [filter, setFilter] = useState('Alle')
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState<'name' | 'count' | 'category'>('name')

  const { data, isLoading, isError } = useQuery({ queryKey: ['inventory'], queryFn: api.inventory })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorMessage message="Inventar konnte nicht geladen werden." />

  let items = data ?? []
  if (filter !== 'Alle') items = items.filter(i => i.category === filter)
  if (search) items = items.filter(i => (i.item_name ?? '').toLowerCase().includes(search.toLowerCase()))

  items = [...items].sort((a, b) => {
    if (sortBy === 'count') return b.stack_count - a.stack_count
    if (sortBy === 'category') return a.category.localeCompare(b.category)
    return (a.item_name ?? '').localeCompare(b.item_name ?? '')
  })

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="text"
          placeholder="Suche…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="gh-input flex-1"
        />
        <div className="flex gap-1.5 overflow-x-auto">
          {CATEGORIES.map(c => {
            const active = filter === c
            return (
              <button
                key={c}
                onClick={() => setFilter(c)}
                className="gh-mono"
                style={{
                  fontSize: 10, padding: '6px 11px', cursor: 'pointer', whiteSpace: 'nowrap',
                  textTransform: 'uppercase', letterSpacing: '0.06em',
                  background: active ? 'rgb(var(--accent-glow) / 0.15)' : 'rgba(0,0,0,0.3)',
                  border: `1px solid ${active ? 'rgb(var(--accent-glow) / 0.4)' : 'var(--border-2)'}`,
                  color: active ? 'var(--accent)' : 'var(--fg-mute)',
                }}
              >
                {c}
              </button>
            )
          })}
        </div>
      </div>

      <Panel eyebrow="Inventar" title={`${items.length} Items`}>
        <div className="overflow-x-auto">
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th onClick={() => setSortBy('name')} className="gh-eyebrow text-left" style={{ fontSize: 9, padding: '10px 14px', cursor: 'pointer' }}>
                  Item {sortBy === 'name' && '▾'}
                </th>
                <th onClick={() => setSortBy('category')} className="gh-eyebrow text-left" style={{ fontSize: 9, padding: '10px 14px', cursor: 'pointer' }}>
                  Kategorie {sortBy === 'category' && '▾'}
                </th>
                <th onClick={() => setSortBy('count')} className="gh-eyebrow" style={{ fontSize: 9, padding: '10px 14px', cursor: 'pointer', textAlign: 'right' }}>
                  Anzahl {sortBy === 'count' && '▾'}
                </th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, i) => (
                <tr key={`${item.item_key}-${i}`} style={{ borderTop: i > 0 ? '1px solid var(--hairline)' : 'none' }}>
                  <td style={{ padding: '9px 14px', fontSize: 12.5, color: '#fff' }}>{item.item_name ?? item.item_key}</td>
                  <td className="gh-mono" style={{ padding: '9px 14px', fontSize: 11, color: CAT_COLOR[item.category] ?? 'var(--fg-mute)' }}>{item.category}</td>
                  <td className="gh-mono" style={{ padding: '9px 14px', fontSize: 12, color: 'var(--fg-dim)', textAlign: 'right' }}>{item.stack_count}</td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr><td colSpan={3} className="gh-eyebrow" style={{ padding: '32px 14px', textAlign: 'center' }}>Keine Items gefunden</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  )
}
