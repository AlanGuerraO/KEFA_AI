import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import EmptyState from '../components/EmptyState';
import Icon from '../components/Icon';
import { useActivity } from '../context/ActivityContext';
import { RESULT_LABELS } from '../services/assistantResults';

const formatter = new Intl.DateTimeFormat('es-MX', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
const tabs = [
  { value: 'all', label: 'Todas' },
  { value: 'prepared', label: 'Preparadas' },
  { value: 'confirmation', label: 'Por confirmar' },
  { value: 'error', label: 'Con error' },
];
export default function Activity() {
  const { entries, clearHistory } = useActivity();
  const [filter, setFilter] = useState('all');
  const [query, setQuery] = useState('');
  const selected = useMemo(() => entries.filter(entry => {
    const matchesStatus = filter === 'all' || (filter === 'error' ? ['error', 'rejected', 'interrupted'].includes(entry.status) : entry.status === filter);
    const matchesText = `${entry.prompt} ${(entry.results || []).map(item => item.tool || '').join(' ')}`.toLowerCase().includes(query.toLowerCase());
    return matchesStatus && matchesText;
  }).reverse(), [entries, filter, query]);

  function exportHistory() {
    const safe = entries.map(({ id, createdAt, prompt, status, results, error }) => ({ id, createdAt, prompt, status, results, error }));
    const blob = new Blob([JSON.stringify(safe, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url; anchor.download = 'kefa-actividad-sesion.json'; document.body.appendChild(anchor); anchor.click(); anchor.remove();
    URL.revokeObjectURL(url);
  }
  function clear() {
    if (window.confirm('¿Borrar el historial local? Esto no cancela operaciones externas.')) clearHistory();
  }
  return <><PageHeader eyebrow="SEGUIMIENTO" title="Actividad" description="Consulta las instrucciones y decisiones registradas durante tu sesión en esta pestaña." actions={<Link to="/conversaciones" className="btn btn-primary"><Icon name="plus" size={17}/> Nueva instrucción</Link>}/>
    <section className="card activity-intro"><span className="illustration-square"><Icon name="activity" size={26}/></span><div><h2>Registro transparente</h2><p>La API actual no ofrece un historial persistente. Los registros de esta vista son locales al navegador y se eliminan al cerrar sesión; no garantizan que una herramienta se haya ejecutado.</p></div><span className="mini-tag">Solo sesión actual</span></section>
    <section className="card activity-board"><div className="panel-heading"><div><h2>Registro de solicitudes</h2><p>{entries.length} {entries.length === 1 ? 'solicitud' : 'solicitudes'} registradas durante la sesión.</p></div><div className="activity-tools"><button type="button" className="btn btn-secondary" onClick={exportHistory} disabled={!entries.length}><Icon name="copy" size={16}/> Exportar JSON</button><button type="button" className="btn btn-quiet" onClick={clear} disabled={!entries.length}>Borrar</button></div></div>
      <div className="activity-controls"><div className="activity-tabs" role="group" aria-label="Filtrar por estado">{tabs.map(tab => <button key={tab.value} type="button" aria-pressed={filter === tab.value} className={filter === tab.value ? 'is-selected' : ''} onClick={() => setFilter(tab.value)}>{tab.label}</button>)}</div><label className="activity-search"><Icon name="search" size={18}/><span className="sr-only">Buscar en historial</span><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Buscar instrucción o herramienta"/></label></div>
      {selected.length === 0 ? <EmptyState icon="clipboard" title={entries.length ? 'No hay resultados para este filtro' : 'Aún no hay solicitudes'} description={entries.length ? 'Prueba otro estado o escribe una búsqueda diferente.' : 'Envía una instrucción desde Conversaciones para verla aquí.'} actions={<Link className="btn btn-secondary" to="/conversaciones">Ir al asistente <Icon name="arrow" size={16}/></Link>}/> : <div className="activity-list">{selected.map(entry => <article className="activity-row" key={entry.id}><span className={`activity-row-icon activity-row-icon--${entry.status}`}><Icon name={entry.status === 'error' || entry.status === 'rejected' ? 'alert' : 'message'} size={19}/></span><div className="activity-row-content"><strong>{entry.prompt}</strong><div className="activity-row-meta"><span>{formatter.format(new Date(entry.createdAt))}</span><span className={`result-pill result-pill--${entry.status}`}>{RESULT_LABELS[entry.status] || entry.status}</span>{entry.results?.[0]?.tool && <code>{entry.results[0].tool}</code>}</div>{entry.error && <p className="error-copy">{entry.error}</p>}</div><Link className="activity-row-link" to="/conversaciones" aria-label="Ver conversación"><Icon name="arrow" size={18}/></Link></article>)}</div>}
    </section>
  </>;
}
