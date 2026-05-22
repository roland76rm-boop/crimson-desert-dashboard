export default function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="gh-card" style={{ padding: 16, borderLeft: '2px solid var(--bad)' }}>
      <div className="gh-eyebrow" style={{ color: 'var(--bad)' }}>Fehler</div>
      <p style={{ fontSize: 12.5, color: 'var(--fg-dim)', marginTop: 6 }}>{message}</p>
    </div>
  )
}
