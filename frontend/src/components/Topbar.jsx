import StatusDot from './StatusDot';
import ThemeToggle from './ThemeToggle';

const WEEKDAY_FORMAT = new Intl.DateTimeFormat('es-MX', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
});

export default function Topbar({ userName = 'Estefanía' }) {
  const today = WEEKDAY_FORMAT.format(new Date());
  const todayCapitalized = today.charAt(0).toUpperCase() + today.slice(1);
  const initial = userName.charAt(0).toUpperCase();

  return (
    <div className="topbar">
      <div>
        <h1>Hola, {userName}</h1>
        <p className="subtitle">{todayCapitalized}</p>
      </div>

      <div className="topbar-actions">
        <StatusDot />
        <ThemeToggle />
        <button type="button" className="iconbtn" aria-label="Notificaciones">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
            <path d="M18 16c-1.6-1.4-2-3.3-2-6a4 4 0 0 0-8 0c0 2.7-.4 4.6-2 6h12Z" />
            <path d="M10 19a2 2 0 0 0 4 0" />
          </svg>
        </button>
        <div className="user-pill">
          <span className="avatar">{initial}</span>
          <span>{userName}</span>
        </div>
      </div>
    </div>
  );
}
