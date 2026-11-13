import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import StatusDot from './StatusDot';
import ThemeToggle from './ThemeToggle';
import Icon from './Icon';
const TITLES = {'/dashboard':'Resumen','/conversaciones':'Conversaciones','/actividad':'Actividad','/integraciones':'Integraciones','/configuracion':'Configuración','/cuenta':'Mi cuenta'};
const dateFormat = new Intl.DateTimeFormat('es-MX', {weekday:'long', day:'numeric', month:'long', year:'numeric'});
export default function Topbar({ openMenu }) {
  const { user } = useAuth();
  const { pathname } = useLocation();
  return <header className="topbar">
    <div className="topbar-start"><button className="menu-toggle iconbtn" onClick={openMenu} type="button" aria-label="Abrir menú"><Icon name="menu"/></button><div className="breadcrumb"><span>Espacio personal</span><Icon name="chevron" size={15}/><strong>{TITLES[pathname] || 'KEFA AI'}</strong></div></div>
    <div className="topbar-actions"><span className="topbar-date">{dateFormat.format(new Date())}</span><StatusDot/><ThemeToggle/><Link to="/cuenta" className="topbar-avatar" aria-label={`Ir a la cuenta de ${user?.username || 'usuario'}`}>{(user?.username || 'U').slice(0,1).toUpperCase()}</Link></div>
  </header>;
}
