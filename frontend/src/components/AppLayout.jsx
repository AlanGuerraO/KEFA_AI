import { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  useEffect(() => { setSidebarOpen(false); }, [location.pathname]);
  useEffect(() => {
    if (!sidebarOpen) return;
    const onKeyDown = (event) => {
      if (event.key === 'Escape') setSidebarOpen(false);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [sidebarOpen]);
  return (
    <div className="app-shell">
      <a className="skip-link" href="#contenido">Saltar al contenido</a>
      <Sidebar open={sidebarOpen} close={() => setSidebarOpen(false)} activePath={location.pathname} />
      {sidebarOpen && <button className="sidebar-scrim" type="button" aria-label="Cerrar menú" onClick={() => setSidebarOpen(false)} />}
      <div className="workspace">
        <Topbar openMenu={() => setSidebarOpen(true)} />
        <main id="contenido" className="content"><Outlet /></main>
      </div>
    </div>
  );
}
