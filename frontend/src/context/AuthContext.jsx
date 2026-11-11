import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { getCurrentUser, loginUser, refreshToken } from '../services/api';

const AuthContext = createContext(null);
const ACCESS_KEY = 'kefa-access-token';
const REFRESH_KEY = 'kefa-refresh-token';

function readSession() {
  try {
    return {
      access: window.sessionStorage.getItem(ACCESS_KEY),
      refresh: window.sessionStorage.getItem(REFRESH_KEY),
    };
  } catch {
    return { access: null, refresh: null };
  }
}
function saveSession(access, refresh) {
  window.sessionStorage.setItem(ACCESS_KEY, access);
  if (refresh) window.sessionStorage.setItem(REFRESH_KEY, refresh);
}
function clearSession() {
  try {
    window.sessionStorage.removeItem(ACCESS_KEY);
    window.sessionStorage.removeItem(REFRESH_KEY);
  } catch { /* El almacenamiento puede estar bloqueado. */ }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState('checking');
  // Impide que una petición que terminó tarde restaure la sesión tras logout.
  const sessionVersion = useRef(0);

  const logout = useCallback(() => {
    sessionVersion.current += 1;
    clearSession();
    setUser(null);
    setStatus('anonymous');
  }, []);

  const authenticate = useCallback(async (identifier, password) => {
    const version = ++sessionVersion.current;
    const tokens = await loginUser(identifier.trim(), password);
    if (version !== sessionVersion.current) return null;
    if (!tokens?.access || !tokens?.refresh) {
      throw new Error('El backend no devolvió los tokens esperados.');
    }
    try {
      saveSession(tokens.access, tokens.refresh);
      const profile = await getCurrentUser(tokens.access);
      if (version !== sessionVersion.current) return null;
      setUser(profile);
      setStatus('authenticated');
      return profile;
    } catch (error) {
      if (version === sessionVersion.current) logout();
      throw error;
    }
  }, [logout]);

  const reloadUser = useCallback(async () => {
    const version = sessionVersion.current;
    const session = readSession();
    if (!session.access) {
      if (version === sessionVersion.current) logout();
      return null;
    }
    try {
      const profile = await getCurrentUser(session.access);
      if (version !== sessionVersion.current) return null;
      setUser(profile);
      setStatus('authenticated');
      return profile;
    } catch (error) {
      if (version !== sessionVersion.current) return null;
      if (error.status === 401 && session.refresh) {
        try {
          const tokens = await refreshToken(session.refresh);
          if (!tokens?.access) throw new Error('No se pudo renovar la sesión.');
          if (version !== sessionVersion.current) return null;
          saveSession(tokens.access, tokens.refresh || session.refresh);
          const profile = await getCurrentUser(tokens.access);
          if (version !== sessionVersion.current) return null;
          setUser(profile);
          setStatus('authenticated');
          return profile;
        } catch {
          if (version === sessionVersion.current) logout();
          return null;
        }
      }
      // Si el servidor no responde, se evita conservar un perfil no verificado.
      logout();
      return null;
    }
  }, [logout]);

  useEffect(() => {
    if (!readSession().access) {
      setStatus('anonymous');
      return;
    }
    reloadUser();
  }, [reloadUser]);

  const value = useMemo(() => ({ user, status, authenticate, logout, reloadUser }),
    [user, status, authenticate, logout, reloadUser]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth debe usarse dentro de AuthProvider.');
  return context;
}
