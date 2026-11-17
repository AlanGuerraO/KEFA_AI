import { Link } from 'react-router-dom';
import Icon from '../components/Icon';
import { useAuth } from '../context/AuthContext';
import { useActivity } from '../context/ActivityContext';
import { RESULT_LABELS } from '../services/assistantResults';

const steps = [
  { title: 'Cuenta y acceso', text: 'Inicio de sesión, JWT y perfil disponibles.', state: 'active', badge: 'Disponible', icon: 'shield' },
  { title: 'Asistente inteligente', text: 'La página envía instrucciones reales al endpoint de Django.', state: 'active', badge: 'Cliente listo', icon: 'sparkles' },
  { title: 'Ejecución de herramientas', text: 'El backend debe enlazar Tool Calling con la ejecución real en n8n.', state: 'pending', badge: 'Por integrar', icon: 'plug' },
];
export default function Dashboard() {
  const { user } = useAuth();
  const { entries } = useActivity();
  const firstName = (user?.username || 'usuario').split(/[_.\s-]/)[0];
  const stats = [
    { label: 'Instrucciones enviadas', value: entries.length, description: 'En esta pestaña', icon: 'message' },
    { label: 'Por confirmar', value: entries.filter(entry => entry.status === 'confirmation').length, description: 'Solicitudes de esta sesión', icon: 'shield' },
    { label: 'Acciones reportadas', value: entries.filter(entry => entry.status === 'reported').length, description: 'Informadas por el backend, no verificadas aquí', icon: 'activity' },
  ];
  return <>
    <section className="welcome-hero"><div className="hero-orbit hero-orbit-a"/><div className="hero-orbit hero-orbit-b"/><div className="hero-content"><span className="hero-eyebrow"><Icon name="sparkles" size={15}/> TU CENTRO DE CONTROL</span><h1>Hola, {firstName}.<br/><span>¿Qué vamos a organizar?</span></h1><p>Envía instrucciones desde el asistente y revisa lo que el sistema ha preparado, autorizado o ejecutado.</p><Link className="btn btn-light" to="/conversaciones">Abrir asistente <Icon name="arrow" size={18}/></Link></div><div className="hero-art" aria-hidden="true"><span className="orbit-dot orbit-dot-one"/><span className="orbit-dot orbit-dot-two"/><span className="hero-art-center"><Icon name="sparkles" size={44}/></span></div></section>
    <div className="section-heading"><div><h2>Tu actividad</h2><p>Resumen local de las solicitudes enviadas durante esta sesión.</p></div><span className="outline-tag"><Icon name="info" size={15}/> Datos de sesión</span></div>
    <section className="stat-grid" aria-label="Resumen de actividad">{stats.map(item => <article className="card stat-card" key={item.label}><div className="stat-top"><span>{item.label}</span><span className="icon-square"><Icon name={item.icon} size={20}/></span></div><strong className="stat-value">{item.value}</strong><p>{item.description}</p></article>)}</section>
    <div className="dashboard-columns"><section className="card panel-card"><div className="panel-heading"><div><h2>Estado de la integración</h2><p>Qué está listo y qué falta para ejecutar acciones reales.</p></div><Icon name="activity" size={20}/></div><div className="progress-list">{steps.map(item => <div className="progress-item" key={item.title}><span className={`progress-icon progress-icon--${item.state}`}><Icon name={item.icon} size={19}/></span><div className="progress-info"><strong>{item.title}</strong><p>{item.text}</p></div><span className={`mini-tag ${item.state === 'active' ? 'mini-tag--ready' : ''}`}>{item.badge}</span></div>)}</div></section>
    <section className="card panel-card"><div className="panel-heading"><div><h2>{entries.length ? 'Últimas instrucciones' : 'Empieza con una idea'}</h2><p>{entries.length ? 'Historial local de esta pestaña.' : 'Ejemplos de instrucciones para el asistente.'}</p></div><Icon name="bolt" size={20}/></div>{entries.length ? <div className="dashboard-recent">{entries.slice(-3).reverse().map(item => <Link key={item.id} to="/conversaciones"><span className="suggestion-icon"><Icon name="message" size={18}/></span><span><strong>{item.prompt}</strong><small>{RESULT_LABELS[item.status] || item.status}</small></span><Icon name="arrow" size={17}/></Link>)}</div> : <div className="suggestion-list"><Link to="/conversaciones" state={{ example: 'Agenda una reunión de equipo mañana a las 5 de la tarde.' }}><span className="suggestion-icon"><Icon name="calendar" size={19}/></span><span>Agendar una reunión</span><Icon name="arrow" size={17}/></Link><Link to="/conversaciones" state={{ example: 'Crea una tarea para preparar la presentación del viernes.' }}><span className="suggestion-icon"><Icon name="tasks" size={19}/></span><span>Preparar una tarea</span><Icon name="arrow" size={17}/></Link><Link to="/integraciones"><span className="suggestion-icon"><Icon name="plug" size={19}/></span><span>Explorar integraciones</span><Icon name="arrow" size={17}/></Link></div>}<p className="panel-footnote">Una herramienta preparada no equivale a una acción ejecutada en Google.</p></section></div>
  </>;
}
