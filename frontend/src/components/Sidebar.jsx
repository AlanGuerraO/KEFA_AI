import { NavLink } from 'react-router-dom';
import Logo from './Logo';

function navClass({ isActive }) {
  return isActive ? 'navbtn active' : 'navbtn';
}

export default function Sidebar() {
  return (
    <div className="sidebar">
      <div className="brand">
        <Logo />
        <span className="brand-name">KEFA AI</span>
      </div>

      <nav className="nav-group">
        <NavLink to="/dashboard" className={navClass}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
            <rect x="3.5" y="3.5" width="7" height="7" rx="1.5" />
            <rect x="13.5" y="3.5" width="7" height="7" rx="1.5" />
            <rect x="3.5" y="13.5" width="7" height="7" rx="1.5" />
            <rect x="13.5" y="13.5" width="7" height="7" rx="1.5" />
          </svg>
          Dashboard
        </NavLink>

        <NavLink to="/conversaciones" className={navClass}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
            <path d="M4 5.5h16v10.5a1.5 1.5 0 0 1-1.5 1.5H9l-4 3.5V17.5A1.5 1.5 0 0 1 4 16V5.5Z" />
          </svg>
          Conversaciones
        </NavLink>

        <NavLink to="/configuracion" className={navClass}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
            <line x1="4" y1="7" x2="20" y2="7" />
            <circle cx="14" cy="7" r="2" />
            <line x1="4" y1="12.5" x2="20" y2="12.5" />
            <circle cx="9" cy="12.5" r="2" />
            <line x1="4" y1="18" x2="20" y2="18" />
            <circle cx="16" cy="18" r="2" />
          </svg>
          Configuración
        </NavLink>
      </nav>

      <div className="nav-group nav-group--footer">
        <NavLink to="/cuenta" className={navClass}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
            <circle cx="12" cy="8.5" r="3.3" />
            <path d="M5 19.2c1.3-3.1 4-4.7 7-4.7s5.7 1.6 7 4.7" />
          </svg>
          Mi cuenta
        </NavLink>

        <NavLink to="/login" className="navbtn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
            <path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h6A1.5 1.5 0 0 1 18 5.5v13a1.5 1.5 0 0 1-1.5 1.5h-6A1.5 1.5 0 0 1 9 18.5V17" />
            <path d="M13 12H4m0 0 2.8-2.6M4 12l2.8 2.6" />
          </svg>
          Cerrar sesión
        </NavLink>
      </div>
    </div>
  );
}
