import { Link } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import Icon from '../components/Icon';

const services = [
  { name: 'Google Tasks', type: 'Productividad', icon: 'tasks', text: 'Crea tareas a partir de instrucciones naturales, mediante n8n y permisos definidos en Django.', support: 'Workflow disponible', status: 'Verificación por cuenta pendiente', checklist: ['OAuth autorizado en la instancia n8n', 'Webhook activo y respuesta verificable', 'Permiso kefa_tasks_write en Django'] },
  { name: 'Google Calendar', type: 'Calendario', icon: 'calendar', text: 'Agenda eventos cuando exista autorización y la herramienta devuelva un resultado comprobable.', support: 'Workflow disponible', status: 'Verificación por cuenta pendiente', checklist: ['OAuth autorizado en n8n', 'Workflow de Calendar probado', 'Permiso kefa_calendar_write en Django'] },
  { name: 'Telegram', type: 'Mensajería', icon: 'telegram', text: 'Canal para enviar órdenes y recibir actualizaciones del asistente.', support: 'Integración en desarrollo', status: 'Sin conexión verificable', checklist: ['Bot configurado por el equipo', 'Identidad de usuario asociada de forma segura', 'Webhook con autenticación comprobada'] },
  { name: 'Notion', type: 'Documentación', icon: 'clipboard', text: 'Gestiona páginas de Notion cuando se habilite el flujo correspondiente.', support: 'Fase posterior', status: 'Sin conexión', checklist: ['Integración autorizada', 'Herramientas del catálogo implementadas', 'Acceso por usuario validado'] },
];
export default function Integrations() {
  return <><PageHeader eyebrow="ECOSISTEMA" title="Integraciones" description="Conoce qué servicios contempla el proyecto y qué falta para conectarlos de forma segura." actions={<Link to="/conversaciones" className="btn btn-primary">Abrir asistente <Icon name="arrow" size={17}/></Link>}/>
    <section className="callout"><span className="callout-icon"><Icon name="shield" size={22}/></span><div><strong>Estado de configuración, no de sesión OAuth</strong><p>Esta página no tiene todavía un endpoint que consulte las conexiones del usuario. Tener un workflow en n8n no significa que tu cuenta personal esté conectada ni que una acción ya se pueda ejecutar.</p></div></section>
    <div className="integration-grid">{services.map(service => <article className="card integration-card integration-detailed" key={service.name}>
      <div className="integration-head"><span className="integration-icon"><Icon name={service.icon} size={25}/></span><span className="mini-tag">{service.support}</span></div><p className="integration-type">{service.type}</p><h2>{service.name}</h2><p>{service.text}</p><div className="integration-state"><Icon name="info" size={16}/>{service.status}</div>
      <h3 className="integration-subtitle">Para habilitarla</h3><ul className="integration-requirements">{service.checklist.map(item => <li key={item}><Icon name="check" size={15}/>{item}</li>)}</ul>
      <div className="integration-footer"><Icon name="lock" size={16}/><span>La conexión debe realizarse desde un flujo autorizado, nunca con contraseñas introducidas en esta pantalla.</span></div>
    </article>)}</div>
    <section className="integration-help card"><div><h2>¿Ya probaron el workflow en n8n?</h2><p>El siguiente paso es verificar el webhook desde Django, validar los permisos del usuario y presentar el identificador de la tarea creada. Hasta entonces, el frontend mostrará las operaciones como preparadas.</p></div><Link to="/configuracion" className="btn btn-secondary">Comprobar backend <Icon name="arrow" size={17}/></Link></section>
  </>;
}
