interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  accent?: 'crimson' | 'gold' | 'default'
}

export default function StatCard({ label, value, sub, accent = 'default' }: StatCardProps) {
  const accentColor = {
    crimson: 'text-crimson',
    gold: 'text-gold',
    default: 'text-slate-200',
  }[accent]

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <p className="text-slate-400 text-xs uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-2xl font-bold ${accentColor}`}>{value}</p>
      {sub && <p className="text-slate-500 text-xs mt-1">{sub}</p>}
    </div>
  )
}
