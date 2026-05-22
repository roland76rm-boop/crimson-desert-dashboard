import { NavLink, Outlet } from 'react-router-dom'

const links = [
  { to: '/', label: 'Übersicht' },
  { to: '/inventory', label: 'Inventar' },
  { to: '/equipment', label: 'Equipment' },
  { to: '/quests', label: 'Quests' },
  { to: '/mercenaries', label: 'Söldner' },
  { to: '/timeline', label: 'Timeline' },
  { to: '/upload', label: 'Upload' },
  { to: '/settings', label: 'Einstellungen' },
]

// Im Gaming-Hub eingebettet (?embed=1) → eigene Logo-Zeile ausblenden
const IS_EMBED = typeof window !== 'undefined'
  && new URLSearchParams(window.location.search).get('embed') === '1'

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col" style={{ position: 'relative', zIndex: 1 }}>
      <header
        className="sticky top-0 z-40"
        style={{ background: 'rgba(20,20,31,0.92)', backdropFilter: 'blur(12px)', borderBottom: '1px solid var(--border)' }}
      >
        <div
          className="max-w-7xl mx-auto flex items-center gap-3 cd-pad"
          style={{ flexWrap: 'wrap', paddingTop: 10, paddingBottom: 10 }}
        >
          {/* Logo — im Embed ausgeblendet (Hub hat eigenen Header) */}
          {!IS_EMBED && (
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 grid place-items-center text-gold text-base"
                   style={{ background: 'rgb(var(--accent-glow) / 0.1)', border: '1px solid rgb(var(--accent-glow) / 0.3)' }}>
                &#9876;
              </div>
              <div>
                <div className="gh-mono" style={{ fontSize: 9, letterSpacing: '0.2em', color: 'var(--fg-mute)', textTransform: 'uppercase' }}>Gaming Hub</div>
                <h1 className="gh-display" style={{ fontSize: 14, fontWeight: 700, color: '#fff', letterSpacing: '0.04em' }}>Crimson Desert</h1>
              </div>
            </div>
          )}
          <nav className="flex gap-0.5" style={{ overflowX: 'auto', flex: 1, minWidth: 0 }}>
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.to === '/'}
                className={({ isActive }) =>
                  `gh-tab ${isActive ? 'active' : ''}`
                }
                style={{ height: 36 }}
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-7xl mx-auto w-full cd-pad" style={{ paddingTop: 20, paddingBottom: 28 }}>
        <Outlet />
      </main>
      <footer
        className="gh-mono text-center"
        style={{ fontSize: 10, color: 'var(--fg-faint)', padding: '14px 0', borderTop: '1px solid var(--hairline)' }}
      >
        Crimson Desert Dashboard · haus543.at
      </footer>
    </div>
  )
}
