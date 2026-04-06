import { NavLink, Outlet } from 'react-router-dom'

const links = [
  { to: '/', label: 'Übersicht' },
  { to: '/inventory', label: 'Inventar' },
  { to: '/equipment', label: 'Equipment' },
  { to: '/quests', label: 'Quests' },
  { to: '/mercenaries', label: 'Söldner' },
  { to: '/timeline', label: 'Timeline' },
  { to: '/upload', label: '⬆ Upload' },
  { to: '/settings', label: 'Einstellungen' },
]

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">&#9876;</span>
            <h1 className="text-xl font-bold text-gold">Crimson Desert</h1>
          </div>
          <nav className="flex gap-1 overflow-x-auto">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.to === '/'}
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded text-sm transition-colors whitespace-nowrap ${
                    isActive
                      ? 'bg-crimson text-white'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700'
                  }`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-6">
        <Outlet />
      </main>
      <footer className="text-center text-slate-600 text-xs py-4 border-t border-slate-800">
        Crimson Desert Dashboard &middot; haus543.at
      </footer>
    </div>
  )
}
