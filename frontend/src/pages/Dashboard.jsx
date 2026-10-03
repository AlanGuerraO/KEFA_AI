import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';

// Datos de ejemplo. Cuando exista el endpoint real (historial de acciones,
// Google Calendar, Google Tasks) esto se reemplaza por el fetch
// correspondiente en services/, manteniendo la misma forma de los datos.
const upcomingEvents = [
  { id: 1, title: 'Reunión de equipo', when: '10:00 a. m.' },
  { id: 2, title: 'Entrega parcial 3', when: 'mañana' },
  { id: 3, title: 'Videollamada con asesor', when: 'viernes' },
];

const recentTasks = [
  { id: 1, title: 'Configurar webhook de Telegram', owner: 'Alan' },
  { id: 2, title: 'Definir prompts del orquestador', owner: 'Fanny' },
  { id: 3, title: 'Diagrama de arquitectura', owner: 'Estefanía' },
];

export default function Dashboard() {
  return (
    <div className="app-shell">
      <Sidebar />

      <main className="content">
        <Topbar />

        <section className="stat-grid" aria-label="Resumen">
          <div className="card">
            <p className="label">Tareas pendientes</p>
            <p className="stat-value">4</p>
          </div>
          <div className="card">
            <p className="label">Eventos hoy</p>
            <p className="stat-value">2</p>
          </div>
          <div className="card">
            <p className="label">Mensajes sin leer</p>
            <p className="stat-value">7</p>
          </div>
        </section>

        <section className="panel-grid">
          <div className="card">
            <h3>Próximos eventos</h3>
            <ul className="list">
              {upcomingEvents.map((event) => (
                <li key={event.id} className="row">
                  <span>{event.title}</span>
                  <span className="pill">{event.when}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="card">
            <h3>Tareas recientes</h3>
            <ul className="list">
              {recentTasks.map((task) => (
                <li key={task.id} className="row">
                  <span>{task.title}</span>
                  <span className="pill">{task.owner}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </main>
    </div>
  );
}
