import { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import Icon from '../components/Icon';
import { useAuth } from '../context/AuthContext';
import { createActivityId, useActivity } from '../context/ActivityContext';
import { sendInstruction, respondToConfirmation } from '../services/api';
import { describeResult, normalizeAssistantResponse, RESULT_LABELS } from '../services/assistantResults';

const examples = [
  { icon: 'tasks', title: 'Crear una tarea', instruction: 'Crea una tarea llamada Revisar avances del proyecto' },
  { icon: 'calendar', title: 'Agendar evento', instruction: 'Agenda una reunión de equipo mañana a las 5 de la tarde' },
  { icon: 'sparkles', title: 'Consultar posibilidades', instruction: '¿Qué herramientas tienes disponibles?' },
];
const shortTime = new Intl.DateTimeFormat('es-MX', { hour: '2-digit', minute: '2-digit' });
const clamp = value => typeof value === 'string' ? value.slice(0, 2000) : '';

function AssistantResult({ entry, onConfirmation, confirmingId }) {
  const results = Array.isArray(entry.results) ? entry.results : [];
  return <div className={`chat-response chat-response--${entry.status}`}>
    <div className="chat-response-heading"><span className="chat-avatar"><Icon name="sparkles" size={17}/></span><strong>KEFA AI</strong><span className={`result-pill result-pill--${entry.status}`}>{RESULT_LABELS[entry.status] || entry.status}</span></div>
    {entry.status === 'processing' && <p className="chat-response-lead"><span className="loading-dot"/> Analizando la instrucción…</p>}
    {entry.status === 'interrupted' && <p className="chat-response-lead">Se interrumpió la vista antes de recibir una respuesta. Comprueba el servicio externo antes de volver a enviar la instrucción para evitar duplicados.</p>}
    {entry.status === 'error' && <p className="chat-response-lead error-copy" role="alert">{entry.error || 'El servidor reportó un error. No se ha confirmado la ejecución.'}</p>}
    {entry.message && <p className="chat-response-lead">{entry.message}</p>}
    {entry.status === 'no_result' && <p className="chat-response-lead">La API respondió, pero no devolvió herramientas ni texto. Esto no significa que se haya ejecutado una acción.</p>}
    {entry.status === 'cancelled' && <p className="chat-response-lead">La solicitud de confirmación fue cancelada. No se ejecutó desde esta pantalla.</p>}
    {results.length > 0 && <div className="tool-result-list">{results.map((result, index) => {
      const needsConfirmation = result.decision === 'request_confirmation' && result.request_id && !entry.resolvedRequests?.includes(result.request_id);
      return <section className="tool-result" key={`${result.request_id || result.tool || 'tool'}-${index}`}>
        <div className="tool-result-head"><span className="tool-result-name"><Icon name="bolt" size={15}/> {result.tool || 'Herramienta no especificada'}</span><span className="tool-status">{result.status || result.decision || 'Sin estado'}</span></div>
        <p>{describeResult(result)}</p>
        {result.reason && !['reject', 'request_confirmation'].includes(result.decision) && <p className="tool-hint">Motivo: {result.reason}</p>}
        {needsConfirmation && <div className="confirmation-panel">
          <div className="confirmation-notice"><Icon name="shield" size={18}/><div><strong>Requiere tu autorización</strong><p>La solicitud vence en cinco minutos. Confirma únicamente si reconoces esta operación. La API actual todavía no puede ejecutar confirmaciones positivas.</p></div></div>
          <div className="confirmation-actions"><button className="btn btn-primary" type="button" disabled={Boolean(confirmingId)} onClick={() => onConfirmation(entry.id, result.request_id, 'confirmar')}><Icon name="check" size={16}/>{confirmingId === result.request_id ? 'Procesando…' : 'Confirmar'}</button><button className="btn btn-secondary" type="button" disabled={Boolean(confirmingId)} onClick={() => onConfirmation(entry.id, result.request_id, 'cancelar')}>Cancelar</button></div>
          {entry.actionErrors?.[result.request_id] && <p className="message-error" role="alert">{entry.actionErrors[result.request_id]}</p>}
        </div>}
        {result.request_id && <span className="request-ref">Solicitud: {result.request_id}</span>}
      </section>;
    })}</div>}
    {entry.status === 'prepared' && <div className="response-disclaimer"><Icon name="info" size={16}/> Preparada no significa ejecutada. El backend debe conectar el ejecutor de n8n y devolver un resultado real.</div>}
    {entry.status === 'reported' && <div className="response-disclaimer"><Icon name="info" size={16}/> El servidor informó un resultado. Comprueba la operación en Google Tasks o Calendar antes de considerarla completada.</div>}
  </div>;
}

export default function Conversations() {
  const location = useLocation();
  const { requestWithAuth } = useAuth();
  const { entries, record, updateEntry, clearHistory } = useActivity();
  const [draft, setDraft] = useState(() => clamp(location.state?.example || ''));
  const [busy, setBusy] = useState(false);
  const [confirmingId, setConfirmingId] = useState(null);
  const [copyStatus, setCopyStatus] = useState('');
  const bottomRef = useRef(null);
  const mountedRef = useRef(true);
  useEffect(() => { mountedRef.current = true; return () => { mountedRef.current = false; }; }, []);
  useEffect(() => { if (location.state?.example) setDraft(clamp(location.state.example)); }, [location.state]);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }, [entries.length]);

  async function handleSend(event) {
    event.preventDefault();
    const text = draft.trim();
    if (!text || busy || text.length > 2000) return;
    const id = createActivityId();
    record({ id, createdAt: new Date().toISOString(), prompt: text, status: 'processing', results: [] });
    setDraft(''); setBusy(true); setCopyStatus('');
    try {
      const response = await requestWithAuth(token => sendInstruction(token, text));
      const normalized = normalizeAssistantResponse(response);
      updateEntry(id, { ...normalized });
    } catch (error) {
      updateEntry(id, { status: 'error', error: error.message || 'No se pudo procesar la instrucción.' });
    } finally {
      if (mountedRef.current) setBusy(false);
    }
  }

  async function handleConfirmation(entryId, requestId, answer) {
    if (confirmingId) return;
    setConfirmingId(requestId);
    try {
      const response = await requestWithAuth(token => respondToConfirmation(token, requestId, answer));
      const entry = entries.find(item => item.id === entryId);
      if (response?.status === 'cancelled' && answer !== 'confirmar') {
        const resolvedRequests = [...(entry?.resolvedRequests || []), requestId];
        updateEntry(entryId, { resolvedRequests, status: 'cancelled', actionErrors: {} });
      } else {
        const normalized = normalizeAssistantResponse(response);
        // El backend debe informar una ejecución real, no simplemente una aceptación.
        updateEntry(entryId, { ...normalized, resolvedRequests: [...(entry?.resolvedRequests || []), requestId] });
      }
    } catch (error) {
      const entry = entries.find(item => item.id === entryId);
      updateEntry(entryId, { actionErrors: { ...entry?.actionErrors, [requestId]: error.message || 'No se pudo procesar la confirmación.' } });
    } finally { if (mountedRef.current) setConfirmingId(null); }
  }

  async function copyDraft() {
    if (!draft.trim()) return;
    try { await navigator.clipboard.writeText(draft.trim()); setCopyStatus('Instrucción copiada.'); }
    catch { setCopyStatus('No se pudo copiar. Selecciona el texto manualmente.'); }
  }
  function clearAll() {
    if (busy || confirmingId) return;
    if (window.confirm('¿Borrar el historial de esta pestaña? Esta acción no borra operaciones ya ejecutadas en servicios externos.')) clearHistory();
  }
  return <>
    <PageHeader eyebrow="ASISTENTE INTELIGENTE" title="Conversaciones" description="Envía instrucciones al orquestador, revisa sus decisiones y autoriza acciones sensibles." actions={<span className="mini-tag">Envío a API habilitado · n8n pendiente</span>}/>
    <div className="assistant-workspace">
      <section className="card chat-panel" aria-label="Conversación con KEFA AI">
        <div className="chat-panel-head"><div className="chat-panel-title"><span className="assistant-icon"><Icon name="sparkles" size={22}/></span><div><h2>Asistente KEFA</h2><p>Canal autenticado con Django y Claude</p></div></div><span className="mini-tag">{entries.length} solicitudes en esta pestaña</span></div>
        <div className="chat-messages" aria-live="polite" aria-relevant="additions text">
          {entries.length === 0 ? <div className="chat-welcome"><span className="chat-welcome-icon"><Icon name="sparkles" size={32}/></span><h3>¿Qué quieres organizar hoy?</h3><p>Escribe una instrucción para que el orquestador la analice. Si una herramienta aún no puede ejecutarse, verás claramente su estado.</p><div className="chat-example-grid">{examples.slice(0,2).map(example => <button type="button" key={example.title} onClick={() => setDraft(example.instruction)}><Icon name={example.icon} size={18}/><span>{example.title}</span><Icon name="arrow" size={15}/></button>)}</div></div> : entries.map(entry => <article key={entry.id} className="chat-exchange" id={`entry-${entry.id}`}>
            <div className="chat-user-row"><div className="chat-user-message"><span>{entry.prompt}</span><time dateTime={entry.createdAt}>{shortTime.format(new Date(entry.createdAt))}</time></div><span className="chat-user-icon"><Icon name="user" size={18}/></span></div>
            <AssistantResult entry={entry} onConfirmation={handleConfirmation} confirmingId={confirmingId}/>
          </article>)}
          <div ref={bottomRef}/>
        </div>
        <form className="chat-compose" onSubmit={handleSend}>
          <label htmlFor="instruction">Escribe tu instrucción</label>
          <textarea id="instruction" value={draft} onChange={event => {setDraft(event.target.value);setCopyStatus('');}} rows={3} maxLength={2000} placeholder="Ej.: Crea una tarea llamada Preparar presentación..." disabled={busy} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} />
          <div className="chat-compose-footer"><span>{draft.length}/2000 · Enter para enviar, Shift + Enter para nueva línea</span><div className="chat-compose-actions"><button type="button" className="btn btn-secondary" disabled={!draft.trim() || busy} onClick={copyDraft} aria-label="Copiar borrador"><Icon name="copy" size={17}/></button><button className="btn btn-primary" type="submit" disabled={!draft.trim() || busy}><Icon name={busy ? 'clock' : 'arrow'} size={17}/>{busy ? 'Procesando…' : 'Enviar instrucción'}</button></div></div>
          {copyStatus && <p role="status" className="inline-message">{copyStatus}</p>}
        </form>
      </section>
      <aside className="assistant-side">
        <section className="card side-panel"><div className="panel-heading"><div><h2>Instrucciones rápidas</h2><p>Selecciona una para editarla.</p></div></div><div className="quick-actions">{examples.map(example => <button type="button" key={example.title} onClick={() => setDraft(example.instruction)} disabled={busy}><span className="suggestion-icon"><Icon name={example.icon} size={19}/></span><span><strong>{example.title}</strong><small>{example.instruction}</small></span><Icon name="plus" size={17}/></button>)}</div></section>
        <section className="card side-panel"><div className="panel-heading"><div><h2>Actividad reciente</h2><p>Guardada solo en esta pestaña.</p></div></div>{entries.length === 0 ? <p className="side-placeholder">Tus solicitudes aparecerán aquí después de enviarlas.</p> : <div className="mini-history">{entries.slice(-5).reverse().map(entry => <a href={`#entry-${entry.id}`} key={entry.id}><span className="mini-history-icon"><Icon name="message" size={16}/></span><span><strong>{entry.prompt}</strong><small>{RESULT_LABELS[entry.status] || entry.status}</small></span></a>)}</div>}<div className="side-actions"><Link to="/actividad" className="btn btn-secondary">Ver actividad <Icon name="arrow" size={16}/></Link><button type="button" className="btn btn-quiet" disabled={!entries.length || busy || Boolean(confirmingId)} onClick={clearAll}>Limpiar historial</button></div></section>
        <section className="side-hint"><Icon name="shield" size={18}/><p>Las instrucciones se envían al backend. El historial visual se guarda solo en esta pestaña y se borra al cerrar sesión. No equivale a una auditoría persistente.</p></section>
      </aside>
    </div>
  </>;
}
