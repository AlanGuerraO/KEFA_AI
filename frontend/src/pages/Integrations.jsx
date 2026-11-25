import { Link } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import Icon from '../components/Icon';

const connectedCapabilities = [
  { name: 'Google Calendar', icon: 'calendar', subtitle: 'Tu tiempo, organizado', description: 'Pídele a KEFA que agende reuniones, clases y actividades. Puedes revisar y editar tus eventos desde Google Calendar.', url: 'https://calendar.google.com/', action: 'Abrir calendario', instruction: 'Agenda un evento llamado Reunión de equipo mañana a las 5 de la tarde, durante una hora.' },
  { name: 'Google Tasks', icon: 'tasks', subtitle: 'Tus pendientes bajo control', description: 'Crea tareas con instrucciones sencillas y consúltalas en Google Tasks para seguir tus pendientes.', url: 'https://tasks.google.com/', action: 'Abrir tareas', instruction: 'Crea una tarea en Google Tasks llamada Preparar mi presentación.' },
];
export default function Integrations() {
  return <><PageHeader eyebrow="TUS HERRAMIENTAS" title="Integraciones" description="Un solo asistente para organizar tus pendientes y eventos." actions={<Link to="/conversaciones" className="btn btn-primary">Hablar con KEFA <Icon name="arrow" size={17}/></Link>}/>
    <section className="kefa-integration-hero"><div><span className="kefa-integration-kicker"><Icon name="sparkles" size={16}/> ORGANIZA SIN CAMBIAR DE APP</span><h2>Lo que necesitas, conectado a tu día.</h2><p>Organiza tareas y eventos desde un solo lugar. KEFA utiliza la cuenta de Google autorizada en este espacio de trabajo.</p></div><span className="kefa-integration-illustration"><Icon name="plug" size={42}/></span></section>
    <div className="integration-grid kefa-integration-grid">{connectedCapabilities.map(service => <article className="card kefa-integration-card" key={service.name}><div className="kefa-integration-top"><span className="integration-icon"><Icon name={service.icon} size={27}/></span><span className="mini-tag">Disponible en este espacio</span></div><p className="integration-type">{service.subtitle}</p><h2>{service.name}</h2><p>{service.description}</p><div className="kefa-integration-actions"><Link className="btn btn-primary" to="/conversaciones" state={{ example: service.instruction }}>Pedirle a KEFA <Icon name="arrow" size={16}/></Link><a className="btn btn-secondary" target="_blank" rel="noreferrer" href={service.url}>{service.action} <Icon name="external" size={15}/></a></div></article>)}</div>
    <section className="card kefa-other-integrations"><div className="settings-title"><span className="icon-square"><Icon name="sparkles"/></span><div><h2>Más posibilidades próximamente</h2><p>Telegram y Notion están contemplados para próximas etapas. Todavía no están disponibles desde esta pantalla.</p></div></div><div className="kefa-upcoming-list"><span><Icon name="telegram" size={17}/> Telegram · Próximamente</span><span><Icon name="clipboard" size={17}/> Notion · Próximamente</span></div></section>
    <p className="kefa-integration-footnote"><Icon name="info" size={16}/> Las conexiones a Google las administra el responsable de este espacio. Todavía no es posible vincular cuentas personales distintas desde esta página.</p>
  </>;
}
