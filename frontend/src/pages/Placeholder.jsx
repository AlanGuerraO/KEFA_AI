import Sidebar from '../components/Sidebar';

/**
 * Pantalla temporal para rutas que todavía no se han construido
 * (Conversaciones, Configuración, Mi cuenta). Se reemplaza página por
 * página siguiendo el desarrollo incremental de la Biblia del Proyecto.
 */
export default function Placeholder({ title }) {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="content">
        <h1>{title}</h1>
        <p className="subtitle">Esta sección todavía no está implementada.</p>
      </main>
    </div>
  );
}
