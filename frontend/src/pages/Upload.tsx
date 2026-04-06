import { useState, useRef } from 'react'

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
    if (!apiKey) { setMessage('API Key fehlt'); return }
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
      setMessage('✅ Save-File erfolgreich hochgeladen und geparst!')
      setResult(data as UploadResult)
    } catch (e) {
      setStatus('error')
      setMessage(`❌ Fehler: ${String(e)}`)
    }
  }

  return (
    <div className="max-w-xl mx-auto py-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gold mb-1">Save-File hochladen</h2>
        <p className="text-slate-400 text-sm">
          Lade deine <code className="text-crimson">save.save</code> Datei hoch um das Dashboard zu aktualisieren.
        </p>
        <p className="text-slate-500 text-xs mt-1">
          Pfad: <code>%LOCALAPPDATA%\Pearl Abyss\CD\save\63006856\slot0\save.save</code>
        </p>
      </div>

      {/* API Key */}
      <div>
        <label className="block text-xs font-semibold text-slate-400 uppercase tracking-widest mb-1">API Key</label>
        <input
          type="password"
          value={apiKey}
          onChange={e => setApiKey(e.target.value)}
          placeholder="API Key eingeben..."
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-crimson"
        />
      </div>

      {/* Dropzone */}
      <div
        onDrop={handleDrop}
        onDragOver={e => e.preventDefault()}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
          file ? 'border-gold bg-gold/5' : 'border-slate-600 hover:border-slate-500 bg-slate-800/50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".save"
          className="hidden"
          onChange={e => setFile(e.target.files?.[0] ?? null)}
        />
        {file ? (
          <div>
            <div className="text-3xl mb-2">📁</div>
            <div className="text-gold font-bold">{file.name}</div>
            <div className="text-slate-400 text-sm">{(file.size / 1024).toFixed(1)} KB</div>
            <button
              onClick={e => { e.stopPropagation(); setFile(null) }}
              className="mt-2 text-xs text-slate-500 hover:text-red-400 transition-colors"
            >
              Datei entfernen
            </button>
          </div>
        ) : (
          <div>
            <div className="text-3xl mb-2">⬆️</div>
            <div className="text-slate-300 font-medium">save.save hierher ziehen</div>
            <div className="text-slate-500 text-sm mt-1">oder klicken zum Auswählen</div>
          </div>
        )}
      </div>

      {/* Upload Button */}
      <button
        onClick={handleUpload}
        disabled={!file || status === 'uploading'}
        className={`w-full py-3 rounded-xl font-bold text-sm transition-all ${
          !file || status === 'uploading'
            ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
            : 'bg-crimson hover:bg-crimson/80 text-white'
        }`}
      >
        {status === 'uploading' ? '⏳ Wird hochgeladen...' : 'Save-File hochladen'}
      </button>

      {/* Status */}
      {message && (
        <div className={`rounded-xl p-4 text-sm font-medium ${
          status === 'success' ? 'bg-green-900/30 text-green-300 border border-green-700' :
          status === 'error'   ? 'bg-red-900/30 text-red-300 border border-red-700' : ''
        }`}>
          {message}
        </div>
      )}

      {/* Ergebnis */}
      {result && (
        <div className="bg-slate-800 rounded-xl p-4 space-y-2">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Geparste Daten</div>
          {result.character_name && (
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Charakter</span>
              <span className="text-gold font-bold">{String(result.character_name)}</span>
            </div>
          )}
          {result.character_level != null && (
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Level</span>
              <span className="text-white font-bold">{result.character_level}</span>
            </div>
          )}
          {result.playtime_seconds != null && result.playtime_seconds > 0 && (
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Spielzeit</span>
              <span className="text-white">{Math.floor(result.playtime_seconds / 3600)}h {Math.floor((result.playtime_seconds % 3600) / 60)}min</span>
            </div>
          )}
          {result.snapshot_id != null && (
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Snapshot ID</span>
              <span className="text-slate-300">#{result.snapshot_id}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
