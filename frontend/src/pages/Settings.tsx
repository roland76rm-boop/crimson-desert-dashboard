import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { formatDate } from '../lib/utils'
import { Panel } from '../components/Panel'

export default function Settings() {
  const health = useQuery({ queryKey: ['health'], queryFn: api.health, refetchInterval: 10_000 })
  const snapshots = useQuery({ queryKey: ['snapshots'], queryFn: () => api.snapshots(1) })

  const isOnline = health.data?.status === 'ok'
  const lastUpload = snapshots.data?.[0]?.uploaded_at

  const rows: { label: string; value: React.ReactNode }[] = [
    {
      label: 'API-Status',
      value: <span className={`gh-pip ${isOnline ? '' : 'bad'}`} style={{ fontSize: 11 }}>{isOnline ? 'Online' : 'Offline'}</span>,
    },
    { label: 'Backend-Service', value: health.data?.service ?? '—' },
    { label: 'Letzter Upload', value: lastUpload ? formatDate(lastUpload) : 'Noch keine Uploads' },
    { label: 'API-URL', value: import.meta.env.VITE_API_URL || '/api (Proxy)' },
  ]

  return (
    <div className="flex flex-col gap-5" style={{ maxWidth: 640 }}>
      <Panel eyebrow="System" title="Verbindung">
        <div>
          {rows.map((r, i) => (
            <div key={r.label} className="flex items-center justify-between px-4 py-3" style={{ borderTop: i > 0 ? '1px solid var(--hairline)' : 'none' }}>
              <span className="gh-eyebrow" style={{ fontSize: 9.5 }}>{r.label}</span>
              <span className="gh-mono" style={{ fontSize: 11.5, color: 'var(--fg-dim)' }}>{r.value}</span>
            </div>
          ))}
        </div>
      </Panel>

      <Panel eyebrow="Pipeline" title="Watcher-Status">
        <p style={{ padding: 16, fontSize: 12, color: 'var(--fg-mute)', lineHeight: 1.6 }}>
          Der File-Watcher läuft auf dem Gaming-PC und überwacht den Save-Ordner.
          Sobald das Spiel installiert und der Watcher gestartet ist, erscheinen hier
          automatisch neue Snapshots.
        </p>
      </Panel>
    </div>
  )
}
