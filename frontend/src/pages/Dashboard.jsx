import { Link } from 'react-router-dom';
import Icon from '../components/Icon';
import { useAuth } from '../context/AuthContext';
const indicators = [
 {label:'Conversaciones',value:'—',description:'Pendiente de historial',icon:'message'},
 {label:'Tareas',value:'—',description:'Sin conexión a Google Tasks',icon:'tasks'},
 {label:'Eventos',value:'—',description:'Sin conexión a Calendar',icon:'calendar'},
];
const steps = [
 {title:'Cuenta y acceso',text:'Inicio de sesión y perfil disponibles.',state:'active',badge:'Disponible',icon:'shield'},
 {title:'Asistente inteligente',text:'Pendiente de conectar el orquestador con la API.',state:'pending',badge:'Por integrar',icon:'sparkles'},
 {title:'Servicios y automatizaciones',text:'Se conectarán mediante OAuth y n8n.',state:'pending',badge:'Por integrar',icon:'plug'},
];
export default function Dashboard() {
 const {user}=useAuth();
 const firstName=(user?.username || 'usuario').split(/[_.\s-]/)[0];
 return <>
  <section className="welcome-hero"><div className="hero-orbit hero-orbit-a"/><div className="hero-orbit hero-orbit-b"/><div className="hero-content"><span className="hero-eyebrow"><Icon name="sparkles" size={15}/> TU CENTRO DE CONTROL</span><h1>Hola, {firstName}.<br/><span>Todo empieza aquí.</span></h1><p>Tu espacio para organizar instrucciones, conectar tus servicios y mantener el control de tus actividades.</p><Link className="btn btn-light" to="/conversaciones">Preparar una instrucción <Icon name="arrow" size={18}/></Link></div><div className="hero-art" aria-hidden="true"><span className="orbit-dot orbit-dot-one"/><span className="orbit-dot orbit-dot-two"/><span className="hero-art-center"><Icon name="sparkles" size={44}/></span></div></section>
  <div className="section-heading"><div><h2>Vista general</h2><p>La información se actualizará cuando conectes los servicios.</p></div><span className="outline-tag"><Icon name="info" size={15}/> Datos pendientes</span></div>
  <section className="stat-grid" aria-label="Resumen de datos">{indicators.map(item=><article className="card stat-card" key={item.label}><div className="stat-top"><span>{item.label}</span><span className="icon-square"><Icon name={item.icon} size={20}/></span></div><strong className="stat-value">{item.value}</strong><p>{item.description}</p></article>)}</section>
  <div className="dashboard-columns"><section className="card panel-card"><div className="panel-heading"><div><h2>Estado de tu espacio</h2><p>Qué está listo y qué falta por integrar.</p></div><Icon name="activity" size={20}/></div><div className="progress-list">{steps.map(item=><div className="progress-item" key={item.title}><span className={`progress-icon progress-icon--${item.state}`}><Icon name={item.icon} size={19}/></span><div className="progress-info"><strong>{item.title}</strong><p>{item.text}</p></div><span className={`mini-tag ${item.state==='active'?'mini-tag--ready':''}`}>{item.badge}</span></div>)}</div></section>
  <section className="card panel-card"><div className="panel-heading"><div><h2>Empieza con una idea</h2><p>Ejemplos de lo que podrás solicitarle a KEFA AI.</p></div><Icon name="bolt" size={20}/></div><div className="suggestion-list"><Link to="/conversaciones" state={{ example:'Agenda una reunión de equipo mañana a las 5 de la tarde.' }}><span className="suggestion-icon"><Icon name="calendar" size={19}/></span><span>Agendar una reunión</span><Icon name="arrow" size={17}/></Link><Link to="/conversaciones" state={{ example:'Crea una tarea para preparar la presentación del viernes.' }}><span className="suggestion-icon"><Icon name="tasks" size={19}/></span><span>Preparar una tarea</span><Icon name="arrow" size={17}/></Link><Link to="/integraciones"><span className="suggestion-icon"><Icon name="plug" size={19}/></span><span>Explorar integraciones</span><Icon name="arrow" size={17}/></Link></div><p className="panel-footnote">Estas son ideas de uso. Su ejecución dependerá de las integraciones del MVP.</p></section></div>
 </>;
}
