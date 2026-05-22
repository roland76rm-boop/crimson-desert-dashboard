interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  accent?: 'crimson' | 'gold' | 'default'
}

export default function StatCard({ label, value, sub, accent = 'default' }: StatCardProps) {
  const color = accent === 'gold' ? 'var(--accent)'
    : accent === 'crimson' ? 'var(--bad)'
    : '#fff'
  return (
    <div className="gh-card" style={{ padding: '13px 15px' }}>
      <div className="gh-eyebrow" style={{ fontSize: 9.5 }}>{label}</div>
      <div className="gh-mono" style={{ fontSize: 24, fontWeight: 700, color, lineHeight: 1.1, marginTop: 6 }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: 'var(--fg-mute)', marginTop: 3 }}>{sub}</div>}
    </div>
  )
}
