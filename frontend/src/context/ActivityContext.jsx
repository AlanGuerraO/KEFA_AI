import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { useAuth } from './AuthContext';

const ActivityContext = createContext(null);
const PREFIX = 'kefa-session-history:';
const MAX_ENTRIES = 60;

export function createActivityId() {
  return typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function readEntries(key) {
  if (!key) return [];
  try {
    const parsed = JSON.parse(window.sessionStorage.getItem(key) || '[]');
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(item => item && typeof item.id === 'string').slice(-MAX_ENTRIES)
      .map(item => {
        // Compatibilidad con historial de la versión anterior: `accepted`
        // se guardaba erróneamente bajo el estado visual `prepared`.
        const wasSent = item.status === 'prepared' && Array.isArray(item.results)
          && item.results.some(result => ['accepted', 'queued', 'executing'].includes(result?.status));
        const current = wasSent ? { ...item, status: 'sent' } : item;
        return current.status === 'processing'
          ? { ...current, status: current.execute ? 'uncertain' : 'interrupted', error: current.execute ? 'La pestaña se cerró o recargó sin confirmar el resultado de la ejecución. Verifica el servicio externo antes de reintentar.' : undefined }
          : current;
      });
  } catch { return []; }
}
function persistEntries(key, entries) {
  if (!key) return;
  try { window.sessionStorage.setItem(key, JSON.stringify(entries)); }
  catch { /* No impedir el uso si el navegador limita el almacenamiento. */ }
}
export function ActivityProvider({ children }) {
  const { user } = useAuth();
  const key = user?.id != null ? `${PREFIX}${user.id}` : null;
  const [state, setState] = useState(() => ({ key, items: readEntries(key) }));
  // Evita mostrar registros del usuario anterior durante un cambio de sesión.
  const entries = state.key === key ? state.items : readEntries(key);
  useEffect(() => {
    if (key !== state.key) setState({ key, items: readEntries(key) });
  }, [key, state.key]);

  const mutate = useCallback(transform => {
    if (!key) return;
    setState(previous => {
      const before = previous.key === key ? previous.items : readEntries(key);
      const after = transform(before).slice(-MAX_ENTRIES);
      persistEntries(key, after);
      return { key, items: after };
    });
  }, [key]);

  const record = useCallback(entry => mutate(items => [...items, entry]), [mutate]);
  const updateEntry = useCallback((id, changes) => mutate(items => items.map(entry => entry.id === id ? { ...entry, ...changes } : entry)), [mutate]);
  const clearHistory = useCallback(() => mutate(() => []), [mutate]);
  const value = useMemo(() => ({ entries, record, updateEntry, clearHistory }), [entries, record, updateEntry, clearHistory]);
  return <ActivityContext.Provider value={value}>{children}</ActivityContext.Provider>;
}
export function useActivity() {
  const context = useContext(ActivityContext);
  if (!context) throw new Error('useActivity necesita ActivityProvider.');
  return context;
}
