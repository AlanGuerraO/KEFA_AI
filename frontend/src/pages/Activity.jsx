import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import EmptyState from '../components/EmptyState';
import Icon from '../components/Icon';
import { useActivity } from '../context/ActivityContext';
import { actionInfo, RESULT_LABELS } from '../services/assistantResults';

const formatter = new Intl.DateTimeFormat('es-MX', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
const filters = [
  { value: 'all', label: 'Todas' },
  { value: 'sent', label: 'Enviadas' },
  { value: 'attention', label: 'Por revisar' },
  { value: 'message', label: 'Respuestas' },
];
const isAttention = status => ['error', 'rejected', 'interrupted', 'uncertain', 'confirmation'].includes(status);
const isSent = status => ['sent', 'reported', 'verified'].includes(status);
const safeCSV = value => {
  let s = String(value ?? '');
  if (/^[\s]*[=+@-]/.test(s)) s = `'${s}`; // Evita interpretar instrucciones como fórmulas.
  return `"${s.replace(/"/g, '""')}"`;
};
export default function Activity() {
  const { entries, clearHistory } = useActivity();
  const [filter, setFilter] = useState('all');
  const [query, setQuery] = useState('');
  const selected = useMemo(() => entries.filter(entry => {
    const matches = filter === 'all' || (filter === 'sent' && isSent(entry.status)) || (filter === 'attention' && isAttention(entry.status)) || (filter === 'message' && entry.status === 'message');
    return matches && (entry.prompt || '').toLowerCase().includes(query.trim().toLowerCase());
  }).reverse(), [entries, filter, query]);
  function exportHistory() {
    const rows = [['Fecha', 'Instrucción', 'Estado', 'Servicio', 'Detalle'], ...entries.map(entry => [entry.createdAt, entry.prompt, RESULT_LABELS[entry.status] || entry.status, actionInfo(entry.results?.[0]?.tool).name, entry.error || entry.message || ''])];
    const content = '\uFEFF' + rows.map(row => row.map(safeCSV).join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob([content], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url; link.download = 'kefa-actividad.csv'; document.body.appendChild(link); link.click(); link.remove();
    URL.revokeObjectURL(url);
  }
  return <><PageHeader eyebrow="TU HISTORIAL" title="Actividad" description="Consulta lo que le has pedido a KEFA en esta sesión." actions={<Link to="/conversaciones" className="btn btn-primary"><Icon name="plus" size={17}/> Nueva conversación</Link>}/>
    <section className="card activity-intro"><span className="illustration-square"><Icon name="activity" size={26}/></span><div><h2>Tus solicitudes, siempre claras</h2><p>Aquí puedes revisar mensajes y respuestas de esta sesión. Para comprobar una tarea o evento creado, abre su aplicación de Google.</p></div><span className="mini-tag">Sesión actual</span></section>
    <section className="card activity-board"><div className="panel-heading"><div><h2>Movimientos recientes</h2><p>{entries.length} {entries.length === 1 ? 'solicitud' : 'solicitudes'} en esta sesión.</p></div><div className="activity-tools"><button type="button" className="btn btn-secondary" onClick={exportHistory} disabled={!entries.length}><Icon name="clipboard" size={16}/> Descargar historial</button><button type="button" className="btn btn-quiet" onClick={() => { if (window.confirm('¿Borrar la actividad de esta sesión? Tus tareas y eventos en Google no se borrarán.')) clearHistory(); }} disabled={!entries.length}>Borrar</button></div></div>
      <div className="activity-controls"><div className="activity-tabs" role="group" aria-label="Filtrar por estado">{filters.map(item => <button key={item.value} type="button" aria-pressed={filter === item.value} className={filter === item.value ? 'is-selected' : ''} onClick={() => setFilter(item.value)}>{item.label}</button>)}</div><label className="activity-search"><Icon name="search" size={18}/><span className="sr-only">Buscar instrucciones</span><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Buscar una solicitud"/></label></div>
      {selected.length === 0 ? <EmptyState icon="clipboard" title={entries.length ? 'No encontramos coincidencias' : 'Todavía no hay actividad'} description={entries.length ? 'Prueba con otro filtro o una búsqueda diferente.' : 'Empieza una conversación para ver tus solicitudes aquí.'} actions={<Link className="btn btn-secondary" to="/conversaciones">Hablar con KEFA <Icon name="arrow" size={16}/></Link>}/> : <div className="activity-list">{selected.map(entry => { const meta = actionInfo(entry.results?.[0]?.tool); return <article className="activity-row" key={entry.id}><span className={`activity-row-icon activity-row-icon--${entry.status}`}><Icon name={isAttention(entry.status) ? 'alert' : meta.icon} size={19}/></span><div className="activity-row-content"><strong>{entry.prompt}</strong><div className="activity-row-meta"><span>{formatter.format(new Date(entry.createdAt))}</span><span className={`result-pill result-pill--${entry.status}`}>{RESULT_LABELS[entry.status] || 'Respuesta recibida'}</span>{meta.kind !== 'other' && <span>{meta.shortName}</span>}</div>{entry.error && <p className="error-copy">{entry.error}</p>}</div><Link className="activity-row-link" to="/conversaciones" aria-label="Ver conversaciones"><Icon name="arrow" size={18}/></Link></article>; })}</div>}
    </section>
  </>;
}
