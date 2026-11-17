import { NavLink, useNavigate } from 'react-router-dom';
import Logo from './Logo';
import Icon from './Icon';
import { useAuth } from '../context/AuthContext';
const primary = [
  { to: '/dashboard', label: 'Resumen', icon: 'grid' },
  { to: '/conversaciones', label: 'Conversaciones', icon: 'message' },
  { to: '/actividad', label: 'Actividad', icon: 'activity' },
  { to: '/integraciones', label: 'Integraciones', icon: 'plug' },
];
const secondary = [
  { to: '/configuracion', label: 'Configuración', icon: 'settings' },
  { to: '/cuenta', label: 'Mi cuenta', icon: 'user' },
];
export default function Sidebar({ open, close }) {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  function handleLogout() { close(); logout(); navigate('/login', { replace: true }); }
  const renderLink = ({ to, label, icon }) => <NavLink key={to} to={to} onClick={close} className={({ isActive }) => `navbtn ${isActive ? 'active' : ''}`}><Icon name={icon} size={19}/><span>{label}</span></NavLink>;
  return <aside className={`sidebar ${open ? 'sidebar--open' : ''}`} aria-label="Menú principal">
    <div className="sidebar-header"><NavLink to="/dashboard" className="brand" onClick={close}><span className="brand-icon"><Logo size={26}/></span><span className="brand-copy"><strong>KEFA<span>AI</span></strong><small>Personal workspace</small></span></NavLink><button className="mobile-close" onClick={close} type="button" aria-label="Cerrar menú"><Icon name="close" /></button></div>
    <nav className="sidebar-nav" aria-label="Navegación principal"><p className="nav-caption">ESPACIO DE TRABAJO</p>{primary.map(renderLink)}<p className="nav-caption nav-caption--second">PREFERENCIAS</p>{secondary.map(renderLink)}</nav>
    <div className="sidebar-bottom"><div className="sidebar-tip"><span className="sidebar-tip-icon"><Icon name="sparkles" size={18} /></span><strong>Tu asistente, a tu ritmo.</strong><p>Prepara instrucciones y reúne tus servicios en un solo lugar.</p><NavLink to="/conversaciones" onClick={close}>Abrir conversaciones <Icon name="arrow" size={15}/></NavLink></div><button type="button" className="sidebar-user" onClick={handleLogout} title="Cerrar sesión"><span className="avatar">{(user?.username || 'U').slice(0,1).toUpperCase()}</span><span className="sidebar-user-copy"><strong>{user?.username || 'Usuario'}</strong><small>Cerrar sesión</small></span><Icon name="logout" size={18}/></button></div>
  </aside>;
}
