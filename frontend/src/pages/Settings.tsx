import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { formatDate } from '../lib/utils'

export default function Settings() {
  const health = useQuery({ queryKey: ['health'], queryFn: api.health, refetchInterval: 10_000 })
  const snapshots = useQuery({ queryKey: ['snapshots'], queryFn: () => api.snapshots(1) })

  const isOnline = health.data?.status === 'ok'
  const lastUpload = snapshots.data?.[0]?.uploaded_at

  return (
    <div className="space-y-6 max-w-2xl">
      <h2 className="text-lg font-bold text-gold">Einstellungen</h2>

      <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-slate-400">API-Status</span>
          <span className={`flex items-center gap-2 text-sm font-medium ${isOnline ? 'text-green-400' : 'text-crimson'}`}>
            <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-400' : 'bg-crimson'}`} />
            {isOnline ? 'Online' : 'Offline'}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-slate-400">Backend-Service</span>
          <span className="text-sm text-slate-300">{health.data?.service ?? '—'}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-slate-400">Letzter Upload</span>
          <span className="text-sm text-slate-300">{lastUpload ? formatDate(lastUpload) : 'Noch keine Uploads'}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-slate-400">API-URL</span>
          <span className="text-sm text-slate-500 font-mono">{import.meta.env.VITE_API_URL || '/api (Proxy)'}</span>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
        <h3 className="text-sm font-medium text-slate-400 mb-3">Watcher-Status</h3>
        <p className="text-slate-500 text-sm">
          Der File-Watcher läuft auf dem Gaming-PC und überwacht den Save-Ordner.
          Sobald das Spiel installiert und der Watcher gestartet ist, erscheinen hier automatisch neue Snapshots.
        </p>
      </div>
    </div>
  )
}
