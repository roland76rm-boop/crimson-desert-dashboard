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
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-2.5 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 grid place-items-center bg-gold/10 border border-gold/30 text-gold text-base">
              &#9876;
            </div>
            <div>
              <div className="font-display text-[9px] tracking-[0.2em] text-slate-500 uppercase leading-none">Gaming Hub</div>
              <h1 className="font-display text-sm font-bold text-white tracking-wide leading-tight">Crimson Desert</h1>
            </div>
          </div>
          <nav className="flex gap-1 overflow-x-auto">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.to === '/'}
                className={({ isActive }) =>
                  `px-3 py-1.5 text-xs font-display font-semibold uppercase tracking-wider transition-colors whitespace-nowrap border-b-2 ${
                    isActive
                      ? 'border-gold text-gold'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
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
