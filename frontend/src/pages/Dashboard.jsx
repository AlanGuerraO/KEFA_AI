import { Link } from 'react-router-dom';
import Icon from '../components/Icon';
import { useAuth } from '../context/AuthContext';
import { useActivity } from '../context/ActivityContext';
import { RESULT_LABELS } from '../services/assistantResults';

const starters = [
  { icon: 'tasks', title: 'Organiza tus pendientes', description: 'Crea una tarea y consúltala en Google Tasks.', instruction: 'Crea una tarea en Google Tasks llamada Preparar mi presentación.' },
  { icon: 'calendar', title: 'Reserva un momento', description: 'Agenda reuniones, clases o actividades.', instruction: 'Agenda un evento en mi calendario mañana a las 5 de la tarde durante 1 hora llamado Reunión de equipo.' },
  { icon: 'sparkles', title: 'Pídele una idea a KEFA', description: 'Explora qué puede hacer por ti.', instruction: '¿En qué me puedes ayudar a organizar mi semana?' },
];
export default function Dashboard() {
  const { user } = useAuth();
  const { entries } = useActivity();
  const firstName = (user?.username || 'usuario').split(/[_.\s-]/)[0];
  const stats = [
    { label: 'Conversaciones', value: entries.length, description: 'De esta sesión', icon: 'message' },
    { label: 'Solicitudes enviadas', value: entries.filter(entry => ['sent', 'reported', 'verified'].includes(entry.status)).length, description: 'Acciones por comprobar en Google', icon: 'arrow' },
    { label: 'Necesitan atención', value: entries.filter(entry => ['error', 'uncertain', 'rejected', 'confirmation'].includes(entry.status)).length, description: 'Revisa sus detalles', icon: 'activity' },
  ];
  return <>
    <section className="welcome-hero"><div className="hero-orbit hero-orbit-a"/><div className="hero-orbit hero-orbit-b"/><div className="hero-content"><span className="hero-eyebrow"><Icon name="sparkles" size={15}/> TU DÍA, MÁS SIMPLE</span><h1>Hola, {firstName}.<br/><span>¿Qué organizamos hoy?</span></h1><p>KEFA te ayuda a recordar tus pendientes, planear reuniones y aprovechar mejor tu tiempo.</p><Link className="btn btn-light" to="/conversaciones">Hablar con KEFA <Icon name="arrow" size={18}/></Link></div><div className="hero-art" aria-hidden="true"><span className="orbit-dot orbit-dot-one"/><span className="orbit-dot orbit-dot-two"/><span className="hero-art-center"><Icon name="sparkles" size={44}/></span></div></section>
    <div className="section-heading"><div><h2>Un vistazo a tu actividad</h2><p>Lo que has pedido durante esta sesión.</p></div><span className="outline-tag"><Icon name="clock" size={15}/> Sesión actual</span></div>
    <section className="stat-grid" aria-label="Resumen de actividad">{stats.map(item => <article className="card stat-card" key={item.label}><div className="stat-top"><span>{item.label}</span><span className="icon-square"><Icon name={item.icon} size={20}/></span></div><strong className="stat-value">{item.value}</strong><p>{item.description}</p></article>)}</section>
    <div className="dashboard-columns">
      <section className="card panel-card"><div className="panel-heading"><div><h2>¿Por dónde empezamos?</h2><p>Selecciona una idea o escribe la tuya.</p></div><Icon name="sparkles" size={20}/></div><div className="kefa-start-grid">{starters.map(item => <Link className="kefa-start-item" to="/conversaciones" state={{ example: item.instruction }} key={item.title}><span className="suggestion-icon"><Icon name={item.icon} size={19}/></span><span><strong>{item.title}</strong><small>{item.description}</small></span><Icon name="arrow" size={17}/></Link>)}</div></section>
      <section className="card panel-card"><div className="panel-heading"><div><h2>{entries.length ? 'Tu actividad reciente' : 'Todo en un solo lugar'}</h2><p>{entries.length ? 'Tus últimos mensajes a KEFA.' : 'Organiza tus días desde una conversación.'}</p></div><Icon name="activity" size={20}/></div>{entries.length ? <div className="dashboard-recent">{entries.slice(-4).reverse().map(item => <Link key={item.id} to="/conversaciones"><span className="suggestion-icon"><Icon name="message" size={18}/></span><span><strong>{item.prompt}</strong><small>{RESULT_LABELS[item.status] || 'Respuesta recibida'}</small></span><Icon name="arrow" size={17}/></Link>)}</div> : <div className="kefa-dashboard-empty"><span className="kefa-dashboard-empty-icon"><Icon name="calendar" size={30}/></span><strong>Más tiempo para lo importante</strong><p>Puedes crear tareas, agendar reuniones o hacer preguntas, sin cambiar entre tantas aplicaciones.</p><Link to="/conversaciones" className="btn btn-secondary">Empezar ahora <Icon name="arrow" size={16}/></Link></div>}<p className="panel-footnote">Comprueba los cambios realizados directamente en tu cuenta de Google.</p></section>
    </div>
  </>;
}
