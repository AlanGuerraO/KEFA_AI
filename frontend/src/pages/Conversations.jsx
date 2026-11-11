import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import EmptyState from '../components/EmptyState';
import Icon from '../components/Icon';
const examples = ['Agrega una reunión mañana a las 5:00 p. m.', 'Crea una tarea para estudiar inteligencia artificial.', 'Muéstrame mis eventos de esta semana.'];
export default function Conversations() {
 const location = useLocation();
 const [draft,setDraft] = useState(location.state?.example || '');
 const [message,setMessage] = useState('');
 async function copy() {
   if (!draft.trim()) {setMessage('Escribe primero una instrucción.');return;}
   try { await navigator.clipboard.writeText(draft.trim()); setMessage('Instrucción copiada al portapapeles.'); }
   catch {setMessage('No fue posible copiar. Selecciona el texto manualmente.');}
 }
 return <><PageHeader eyebrow="ASISTENTE" title="Conversaciones" description="Prepara tus solicitudes para KEFA AI. El envío a la IA se habilitará al integrar el orquestador." />
 <div className="conversation-grid"><section className="card conversation-composer"><div className="panel-heading"><div><h2>Nueva instrucción</h2><p>Escribe lo que necesitas con tus propias palabras.</p></div><span className="mini-tag">Modo preparación</span></div><div className="composer-inner"><div className="assistant-intro"><span className="assistant-icon"><Icon name="sparkles" size={23}/></span><div><strong>Hola, soy KEFA AI</strong><p>Cuando la integración esté lista, podré ayudarte a coordinar tareas y eventos. Por ahora puedes preparar tu mensaje.</p></div></div><label className="composer-label" htmlFor="instruction">Tu instrucción</label><textarea id="instruction" className="instruction-input" value={draft} maxLength={2000} onChange={e=>{setDraft(e.target.value);setMessage('')}} placeholder="Ej.: Agenda una reunión el viernes a las 4 de la tarde..." rows={5}/><div className="composer-meta"><span>{draft.length}/2000 caracteres</span><span><Icon name="lock" size={14}/> No se enviará a ningún servicio</span></div><div className="composer-actions"><button className="btn btn-secondary" type="button" onClick={()=>{setDraft('');setMessage('')}} disabled={!draft}>Limpiar</button><button className="btn btn-primary" type="button" onClick={copy} disabled={!draft.trim()}><Icon name="copy" size={17}/> Copiar instrucción</button></div>{message&&<p className="inline-message" role="status">{message}</p>}</div><div className="info-strip"><Icon name="info" size={18}/><p>La ejecución de instrucciones no está disponible en esta versión. No se guardan ni se envían estos borradores al backend.</p></div></section>
 <aside className="conversation-aside"><section className="card panel-card"><div className="panel-heading"><div><h2>Prueba estas ideas</h2><p>Selecciona un ejemplo para editarlo.</p></div></div><div className="example-list">{examples.map(e=><button type="button" key={e} onClick={()=>{setDraft(e);setMessage('')}}><Icon name="plus" size={17}/>{e}</button>)}</div></section><section className="card panel-card"><h2>Historial de conversaciones</h2><EmptyState icon="message" title="Todavía no hay historial" description="Aparecerá aquí cuando el backend registre las conversaciones de forma segura."/></section></aside></div></>;
}
