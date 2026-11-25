import { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import Icon from '../components/Icon';
import { useAuth } from '../context/AuthContext';
import { createActivityId, useActivity } from '../context/ActivityContext';
import { sendAutomaticInstruction, respondToConfirmation } from '../services/api';
import { useVoiceDictation } from '../hooks/useVoiceDictation';
import AssistantFormattedText from '../components/AssistantFormattedText';
import { actionInfo, describeResult, normalizeAssistantResponse, normalizeInstructionError, RESULT_LABELS } from '../services/assistantResults';

const suggestions = [
  { icon: 'tasks', title: 'Crear una tarea', detail: 'Organiza algo que tengas pendiente', instruction: 'Crea una tarea en Google Tasks llamada Revisar los avances del proyecto.', },
  { icon: 'calendar', title: 'Agendar un evento', detail: 'Aparta un espacio en tu calendario', instruction: 'Agenda en mi calendario una reunión de equipo mañana a las 5 de la tarde con duración de 1 hora.', },
  { icon: 'sparkles', title: 'Preguntarle a KEFA', detail: 'Conoce lo que puedes hacer', instruction: '¿En qué puedes ayudarme con mis tareas y eventos?', },
];
const shortTime = new Intl.DateTimeFormat('es-MX', { hour: '2-digit', minute: '2-digit' });
const clamp = value => typeof value === 'string' ? value.slice(0, 2000) : '';
const actionResults = entry => Array.isArray(entry.results) ? entry.results.filter(item => item && item.decision !== 'respond') : [];

function AssistantResult({ entry, confirmingId, onCancelRequest }) {
  const results = actionResults(entry);
  const submitted = entry.status === 'sent' || (entry.status === 'prepared' && results.some(item => item.status === 'accepted'));
  return <div className={`chat-response chat-response--${entry.status}`}>
    <div className="chat-response-heading"><span className="chat-avatar"><Icon name="sparkles" size={17}/></span><strong>KEFA</strong><span className={`result-pill result-pill--${entry.status}`}>{RESULT_LABELS[entry.status] || 'Respuesta disponible'}</span></div>
    {entry.status === 'processing' && <p className="chat-response-lead"><span className="loading-dot"/> Estoy revisando tu solicitud…</p>}
    {entry.status === 'interrupted' && <p className="chat-response-lead">Se interrumpió la comunicación. Puedes volver a consultar sin realizar cambios.</p>}
    {['error', 'uncertain'].includes(entry.status) && <p className="chat-response-lead error-copy" role="alert">{entry.error || 'No se pudo completar la solicitud.'}</p>}
    {entry.status === 'uncertain' && <p className="chat-response-lead">La acción podría haberse realizado. Revisa Google Tasks o Calendar antes de intentarlo de nuevo.</p>}
    {entry.status === 'no_result' && <p className="chat-response-lead">No pude interpretar esa instrucción. Intenta escribirla de otra manera.</p>}
    {entry.status === 'cancelled' && <p className="chat-response-lead">Cancelaste la solicitud. No se envió una nueva acción desde aquí.</p>}
    {entry.message && <AssistantFormattedText text={entry.message}/>}
    {results.length > 0 && <div className="tool-result-list">{results.map((item, index) => {
      const meta = actionInfo(item.tool);
      const requestPending = item.decision === 'request_confirmation' && item.request_id && !entry.resolvedRequests?.includes(item.request_id);
      return <section className="tool-result" key={`${item.request_id || item.tool || 'action'}-${index}`}>
        <div className="tool-result-head"><span className="tool-result-name"><span className="kefa-service-icon"><Icon name={meta.icon} size={18}/></span>{meta.name}</span></div>
        <p>{describeResult(item)}</p>
        {meta.url && ['sent', 'verified', 'reported', 'uncertain'].includes(entry.status) && <a className="kefa-service-link" href={meta.url} target="_blank" rel="noreferrer">Revisar en {meta.kind === 'task' ? 'Google Tasks' : 'Google Calendar'} <Icon name="external" size={15}/></a>}
        {requestPending && <div className="confirmation-panel"><div className="confirmation-notice"><Icon name="shield" size={18}/><div><strong>Hace falta una autorización adicional</strong><p>Por seguridad, esta operación todavía no se puede completar desde el asistente. Puedes cancelar la solicitud.</p></div></div><button type="button" className="btn btn-secondary" disabled={Boolean(confirmingId)} onClick={() => onCancelRequest(entry.id, item.request_id)}>{confirmingId === item.request_id ? 'Cancelando…' : 'Cancelar solicitud'}</button>{entry.actionErrors?.[item.request_id] && <p className="message-error" role="alert">{entry.actionErrors[item.request_id]}</p>}</div>}
      </section>;
    })}</div>}
    {submitted && <p className="response-disclaimer"><Icon name="info" size={16}/> La solicitud fue enviada. KEFA todavía no puede confirmar automáticamente que Google la haya guardado.</p>}
    {entry.status === 'reported' && <p className="response-disclaimer"><Icon name="info" size={16}/> El sistema informó el resultado, pero no recibimos un identificador externo para comprobarlo.</p>}
    {entry.status === 'verified' && <p className="response-disclaimer"><Icon name="checkCircle" size={16}/> El servicio devolvió un identificador. Puedes comprobar el registro desde el enlace.</p>}
  </div>;
}

export default function Conversations() {
  const location = useLocation();
  const { requestWithAuth } = useAuth();
  const { entries, record, updateEntry, clearHistory } = useActivity();
  const [draft, setDraft] = useState(() => clamp(location.state?.example || ''));
  const [busy, setBusy] = useState(false);
  const [confirmingId, setConfirmingId] = useState(null);
  const sendingRef = useRef(false);
  const mountedRef = useRef(true);
  const chatScrollRef = useRef(null);
  const composeRef = useRef(null);
  const voice = useVoiceDictation(setDraft);
  useEffect(() => { mountedRef.current = true; return () => { mountedRef.current = false; }; }, []);
  useEffect(() => { if (location.state?.example) setDraft(clamp(location.state.example)); }, [location.state]);
  useEffect(() => {
    const node = chatScrollRef.current;
    if (node) node.scrollTo({ top: node.scrollHeight, behavior: 'smooth' });
  }, [entries.length, entries[entries.length - 1]?.status]);

  async function dispatch(prompt) {
    if (sendingRef.current || busy) return;
    sendingRef.current = true;
    const id = createActivityId();
    record({ id, createdAt: new Date().toISOString(), prompt, execute: true, status: 'processing', results: [] });
    setDraft(''); setBusy(true);
    try {
      const response = await requestWithAuth(token => sendAutomaticInstruction(token, prompt));
      updateEntry(id, normalizeAssistantResponse(response));
    } catch (error) {
      updateEntry(id, normalizeInstructionError(error, true));
    } finally {
      sendingRef.current = false;
      if (mountedRef.current) setBusy(false);
    }
  }
  function handleSend(event) {
    event.preventDefault();
    const prompt = draft.trim();
    if (!prompt || sendingRef.current || busy || voice.listening || prompt.length > 2000) return;
    dispatch(prompt);
  }
  async function handleCancelRequest(entryId, requestId) {
    if (confirmingId) return;
    setConfirmingId(requestId);
    try {
      const response = await requestWithAuth(token => respondToConfirmation(token, requestId, 'cancelar'));
      if (response?.status !== 'cancelled') throw new Error('No se pudo confirmar la cancelación.');
      const entry = entries.find(item => item.id === entryId);
      const resolvedRequests = [...(entry?.resolvedRequests || []), requestId];
      const remaining = (entry?.results || []).some(item => item.decision === 'request_confirmation' && item.request_id && !resolvedRequests.includes(item.request_id));
      updateEntry(entryId, { resolvedRequests, status: remaining ? 'confirmation' : 'cancelled', actionErrors: {} });
    } catch (error) {
      const entry = entries.find(item => item.id === entryId);
      updateEntry(entryId, { actionErrors: { ...entry?.actionErrors, [requestId]: error.message || 'No se pudo cancelar.' } });
    } finally { if (mountedRef.current) setConfirmingId(null); }
  }
  function useSuggestion(item) {
    if (busy) return;
    setDraft(item.instruction);
    composeRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  function clearAll() {
    if (busy || confirmingId || voice.listening) return;
    if (window.confirm('¿Borrar las conversaciones de esta sesión? Esto no elimina tareas ni eventos de Google.')) clearHistory();
  }
  return <>
    <PageHeader eyebrow="TU ASISTENTE PERSONAL" title="Conversaciones" description="Haz preguntas, dicta tus ideas o pídele que organice tus pendientes automáticamente." actions={<span className="mini-tag"><Icon name="shield" size={14}/> Tu espacio privado</span>}/>
    <div className="assistant-workspace kefa-final-workspace">
      <section className="card chat-panel" aria-label="Conversación con KEFA">
        <div className="chat-panel-head"><div className="chat-panel-title"><span className="assistant-icon"><Icon name="sparkles" size={22}/></span><div><h2>KEFA · Asistente personal</h2><p>Organiza tu día con palabras sencillas</p></div></div><span className="kefa-available-chip"><span className="kefa-available-dot"/> Listo para ayudarte</span></div>
        <div ref={chatScrollRef} className="chat-messages" aria-live="polite" aria-relevant="additions text">
          {entries.length === 0 ? <div className="chat-welcome"><span className="chat-welcome-icon"><Icon name="sparkles" size={32}/></span><h3>Hola, ¿qué hacemos hoy?</h3><p>Pregúntame algo, crea una tarea o agenda un evento. Yo identificaré lo que necesitas, sin cambiar de modo.</p><div className="chat-example-grid">{suggestions.slice(0,2).map(item => <button type="button" key={item.title} onClick={() => useSuggestion(item)}><Icon name={item.icon} size={18}/><span>{item.title}</span><Icon name="arrow" size={15}/></button>)}</div></div> : entries.map(entry => <article key={entry.id} className="chat-exchange" id={`entry-${entry.id}`}>
            <div className="chat-user-row"><div className="chat-user-message"><span>{entry.prompt}</span><time dateTime={entry.createdAt}>{shortTime.format(new Date(entry.createdAt))}</time></div><span className="chat-user-icon"><Icon name="user" size={18}/></span></div>
            <AssistantResult entry={entry} confirmingId={confirmingId} onCancelRequest={handleCancelRequest} />
          </article>)}
        </div>
        <form ref={composeRef} className="chat-compose kefa-compose-final" onSubmit={handleSend}>
          <div className="kefa-compose-top"><label htmlFor="instruction">Escríbele a KEFA</label><span className="kefa-compose-count">{draft.length}/2000</span></div>
          <textarea id="instruction" value={draft} onChange={event => {setDraft(event.target.value);}} rows={3} maxLength={2000} placeholder="Ej.: Crea una tarea para estudiar mañana, o agenda una reunión el viernes…" disabled={busy || voice.listening} onKeyDown={event => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }}/>
          <div className="kefa-compose-controls kefa-compose-auto">
            <span className="kefa-auto-status"><Icon name="sparkles" size={17}/> KEFA decide cómo ayudarte</span>
            <div className="kefa-send-actions">
              <button type="button" className={`btn kefa-mic-btn ${voice.listening ? 'is-listening' : ''}`} onClick={voice.listening ? voice.stop : voice.start} disabled={busy || !voice.supported} aria-pressed={voice.listening} aria-label={voice.listening ? 'Detener dictado' : 'Dictar por micrófono'} title={voice.supported ? (voice.listening ? 'Detener dictado' : 'Dictar por voz') : 'Dictado no disponible en este navegador'}><Icon name={voice.listening ? 'micOff' : 'mic'} size={20}/><span>{voice.listening ? 'Detener' : 'Dictar'}</span></button>
              <button className="btn btn-primary kefa-send" type="submit" disabled={busy || voice.listening || !draft.trim()}><Icon name={busy ? 'clock' : 'arrow'} size={18}/>{busy ? 'Pensando…' : 'Enviar'}</button>
            </div>
          </div>
          {voice.listening && <p className="kefa-voice-status" role="status"><span className="kefa-voice-pulse"/> Escuchando… {voice.interim ? `«${voice.interim}»` : 'Habla con naturalidad; el texto aparecerá arriba.'}</p>}
          {voice.error && <p className="kefa-voice-error" role="alert">{voice.error}</p>}
          <p className="kefa-compose-help"><Icon name="info" size={15}/> Pregunta, pide una tarea o agenda una reunión. Las acciones sencillas se envían directamente; nunca se ejecutan eliminaciones. <span>Revisa el texto dictado antes de enviarlo.</span></p>
        </form>
      </section>
      <aside className="assistant-side kefa-final-side">
        <section className="card side-panel"><div className="panel-heading"><div><h2>Prueba con estas ideas</h2><p>Selecciona una y adáptala a tus planes.</p></div></div><div className="quick-actions">{suggestions.map(item => <button type="button" key={item.title} onClick={() => useSuggestion(item)} disabled={busy || voice.listening}><span className="suggestion-icon"><Icon name={item.icon} size={19}/></span><span><strong>{item.title}</strong><small>{item.detail}</small></span><Icon name="plus" size={17}/></button>)}</div></section>
        <section className="card side-panel"><div className="panel-heading"><div><h2>Tu actividad reciente</h2><p>Solicitudes de esta sesión.</p></div></div>{entries.length === 0 ? <p className="side-placeholder">Cuando le escribas a KEFA, tus solicitudes aparecerán aquí.</p> : <div className="mini-history">{entries.slice(-4).reverse().map(entry => <a href={`#entry-${entry.id}`} key={entry.id}><span className="mini-history-icon"><Icon name="message" size={16}/></span><span><strong>{entry.prompt}</strong><small>{RESULT_LABELS[entry.status] || 'Respuesta recibida'}</small></span></a>)}</div>}<div className="side-actions"><Link to="/actividad" className="btn btn-secondary">Ver actividad <Icon name="arrow" size={16}/></Link><button type="button" className="btn btn-quiet" disabled={!entries.length || busy || voice.listening || Boolean(confirmingId)} onClick={clearAll}>Limpiar</button></div></section>
        <section className="kefa-service-shortcuts"><a href="https://calendar.google.com/" target="_blank" rel="noreferrer"><span><Icon name="calendar" size={19}/> Mi calendario</span><Icon name="external" size={16}/></a><a href="https://tasks.google.com/" target="_blank" rel="noreferrer"><span><Icon name="tasks" size={19}/> Mis tareas</span><Icon name="external" size={16}/></a></section>
        <p className="kefa-session-note"><Icon name="lock" size={16}/> Las conversaciones se guardan en esta sesión del navegador. Tus registros de Google se administran directamente en sus aplicaciones.</p>
      </aside>
    </div>
  </>;
}
