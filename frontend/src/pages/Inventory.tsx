import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const CATEGORIES = ['Alle', 'Equipment', 'Material', 'Consumable', 'Quest', 'Misc']

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

  const catColor: Record<string, string> = {
    Equipment: 'text-gold',
    Material: 'text-blue-400',
    Consumable: 'text-green-400',
    Quest: 'text-crimson-light',
    Misc: 'text-slate-400',
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="text"
          placeholder="Suche..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-crimson flex-1"
        />
        <div className="flex gap-1 overflow-x-auto">
          {CATEGORIES.map(c => (
            <button
              key={c}
              onClick={() => setFilter(c)}
              className={`px-3 py-1.5 rounded text-xs whitespace-nowrap transition-colors ${
                filter === c ? 'bg-crimson text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400 text-xs uppercase tracking-wider">
              <th className="text-left px-4 py-3 cursor-pointer hover:text-slate-200" onClick={() => setSortBy('name')}>
                Item {sortBy === 'name' && '▼'}
              </th>
              <th className="text-left px-4 py-3 cursor-pointer hover:text-slate-200" onClick={() => setSortBy('category')}>
                Kategorie {sortBy === 'category' && '▼'}
              </th>
              <th className="text-right px-4 py-3 cursor-pointer hover:text-slate-200" onClick={() => setSortBy('count')}>
                Anzahl {sortBy === 'count' && '▼'}
              </th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, i) => (
              <tr key={`${item.item_key}-${i}`} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                <td className="px-4 py-2.5 font-medium">{item.item_name ?? item.item_key}</td>
                <td className={`px-4 py-2.5 ${catColor[item.category] ?? 'text-slate-400'}`}>{item.category}</td>
                <td className="px-4 py-2.5 text-right font-mono">{item.stack_count}</td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={3} className="px-4 py-8 text-center text-slate-500">Keine Items gefunden.</td></tr>
            )}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-slate-600">{items.length} Items</p>
    </div>
  )
}
