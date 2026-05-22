import { useState, useRef } from 'react'
import { Panel } from '../components/Panel'

const API_URL = import.meta.env.VITE_API_URL ?? 'https://cd.haus543.at/api'
const API_KEY = import.meta.env.VITE_API_KEY ?? ''

export default function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [apiKey, setApiKey] = useState(API_KEY)
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')
  interface UploadResult { character_name?: string; character_level?: number; playtime_seconds?: number; snapshot_id?: number }
  const [result, setResult] = useState<UploadResult | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (f) setFile(f)
  }

  const handleUpload = async () => {
    if (!file) return
    if (!apiKey) { setMessage('API Key fehlt'); setStatus('error'); return }
    setStatus('uploading')
    setMessage('')
    setResult(null)
    try {
      const form = new FormData()
      form.append('file', file)
      form.append('slot', 'slot0')
      const res = await fetch(`${API_URL}/upload-file`, {
        method: 'POST',
        headers: { 'X-API-Key': apiKey },
        body: form,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail ?? `HTTP ${res.status}`)
      setStatus('success')
      setMessage('Save-File erfolgreich hochgeladen und geparst.')
      setResult(data as UploadResult)
    } catch (e) {
      setStatus('error')
      setMessage(`Fehler: ${String(e)}`)
    }
  }

  return (
    <div className="flex flex-col gap-5" style={{ maxWidth: 560, margin: '0 auto' }}>
      <div>
        <div className="gh-eyebrow-accent">Save-Sync</div>
        <h2 className="gh-display" style={{ fontSize: 22, fontWeight: 700, color: '#fff', margin: '5px 0 6px' }}>
          Save-File hochladen
        </h2>
        <p style={{ fontSize: 12, color: 'var(--fg-mute)', lineHeight: 1.5 }}>
          Lade deine <span className="gh-mono" style={{ color: 'var(--accent)' }}>save.save</span> Datei hoch, um das
          Dashboard zu aktualisieren. Pfad:{' '}
          <span className="gh-mono" style={{ color: 'var(--fg-faint)' }}>%LOCALAPPDATA%\Pearl Abyss\CD\save\…\slot0\save.save</span>
        </p>
      </div>

      <Panel eyebrow="Authentifizierung" title="API Key">
        <div className="p-4">
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder="API Key eingeben…"
            className="gh-input w-full"
          />
        </div>
      </Panel>

      {/* Dropzone */}
      <div
        onDrop={handleDrop}
        onDragOver={e => e.preventDefault()}
        onClick={() => inputRef.current?.click()}
        className="gh-card"
        style={{
          padding: 36, textAlign: 'center', cursor: 'pointer',
          borderStyle: 'dashed',
          borderColor: file ? 'rgb(var(--accent-glow) / 0.5)' : 'var(--border-2)',
          background: file ? 'rgb(var(--accent-glow) / 0.05)' : 'var(--card)',
        }}
      >
        <input ref={inputRef} type="file" accept=".save" className="hidden" onChange={e => setFile(e.target.files?.[0] ?? null)} />
        {file ? (
          <div>
            <div className="gh-display" style={{ fontSize: 14, fontWeight: 700, color: 'var(--accent)' }}>{file.name}</div>
            <div className="gh-mono" style={{ fontSize: 11, color: 'var(--fg-mute)', marginTop: 3 }}>{(file.size / 1024).toFixed(1)} KB</div>
            <button
              onClick={e => { e.stopPropagation(); setFile(null) }}
              className="gh-mono"
              style={{ marginTop: 8, fontSize: 10, color: 'var(--fg-faint)', background: 'none', border: 0, cursor: 'pointer' }}
            >
              Datei entfernen
            </button>
          </div>
        ) : (
          <div>
            <div className="gh-eyebrow">save.save hierher ziehen</div>
            <div className="gh-mono" style={{ fontSize: 11, color: 'var(--fg-faint)', marginTop: 5 }}>oder klicken zum Auswählen</div>
          </div>
        )}
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || status === 'uploading'}
        className="gh-btn gh-btn-primary w-full"
        style={{ height: 40, justifyContent: 'center', opacity: !file || status === 'uploading' ? 0.4 : 1 }}
      >
        {status === 'uploading' ? 'Wird hochgeladen…' : 'Save-File hochladen'}
      </button>

      {message && (
        <div className="gh-card" style={{ padding: 14, borderLeft: `2px solid ${status === 'success' ? 'var(--ok)' : 'var(--bad)'}` }}>
          <span style={{ fontSize: 12.5, color: status === 'success' ? 'var(--ok)' : 'var(--bad)' }}>{message}</span>
        </div>
      )}

      {result && (
        <Panel eyebrow="Ergebnis" title="Geparste Daten">
          <div>
            {[
              result.character_name != null && { label: 'Charakter', value: String(result.character_name), accent: true },
              result.character_level != null && { label: 'Level', value: String(result.character_level) },
              result.playtime_seconds != null && result.playtime_seconds > 0 && {
                label: 'Spielzeit',
                value: `${Math.floor(result.playtime_seconds / 3600)}h ${Math.floor((result.playtime_seconds % 3600) / 60)}min`,
              },
              result.snapshot_id != null && { label: 'Snapshot ID', value: `#${result.snapshot_id}` },
            ].filter(Boolean).map((r, i) => {
              const row = r as { label: string; value: string; accent?: boolean }
              return (
                <div key={i} className="flex justify-between items-center px-4 py-3" style={{ borderTop: i > 0 ? '1px solid var(--hairline)' : 'none' }}>
                  <span className="gh-eyebrow" style={{ fontSize: 9.5 }}>{row.label}</span>
                  <span className="gh-mono" style={{ fontSize: 12, color: row.accent ? 'var(--accent)' : '#fff', fontWeight: 600 }}>{row.value}</span>
                </div>
              )
            })}
          </div>
        </Panel>
      )}
    </div>
  )
}
