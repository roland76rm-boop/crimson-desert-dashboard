import type { ReactNode } from 'react';

/** Panel im Gaming-Hub-Stil: gh-card mit Eyebrow + Titel-Kopf. */
export function Panel({
  eyebrow,
  title,
  headerRight,
  strip,
  className = '',
  children,
}: {
  eyebrow?: string;
  title?: string;
  headerRight?: ReactNode;
  strip?: boolean;
  className?: string;
  children: ReactNode;
}) {
  return (
    <section className={`gh-card ${strip ? 'gh-card-strip' : ''} ${className}`}>
      {(eyebrow || title || headerRight) && (
        <div className="gh-panel-head">
          <div style={{ minWidth: 0 }}>
            {eyebrow && <div className="gh-eyebrow" style={{ fontSize: 9.5 }}>{eyebrow}</div>}
            {title && (
              <div className="gh-display" style={{ fontSize: 14, fontWeight: 700, color: '#fff', marginTop: eyebrow ? 3 : 0 }}>
                {title}
              </div>
            )}
          </div>
          {headerRight && <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>{headerRight}</div>}
        </div>
      )}
      {children}
    </section>
  );
}

/** Kennzahl-Kachel: Eyebrow-Label + große Mono-Zahl. */
export function StatTile({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string | number;
  sub?: string;
  accent?: boolean;
}) {
  return (
    <div className="gh-card" style={{ padding: '13px 15px' }}>
      <div className="gh-eyebrow" style={{ fontSize: 9.5 }}>{label}</div>
      <div className="gh-mono" style={{ fontSize: 24, fontWeight: 700, color: accent ? 'var(--accent)' : '#fff', lineHeight: 1.1, marginTop: 6 }}>
        {value}
      </div>
      {sub && <div style={{ fontSize: 11, color: 'var(--fg-mute)', marginTop: 3 }}>{sub}</div>}
    </div>
  );
}
