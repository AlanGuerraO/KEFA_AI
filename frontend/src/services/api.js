// Cliente HTTP mínimo. Usa fetch nativo: no se introduce axios ni otra
// dependencia hasta que el equipo decida que hace falta.
//
// VITE_API_URL se define en frontend/.env (ver .env.example). Vite solo
// expone al cliente las variables que empiezan con VITE_.

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = new Error(`La petición a ${path} falló con estado ${response.status}`);
    error.status = response.status;
    throw error;
  }

  // El health check y la mayoría de endpoints devuelven JSON.
  const contentType = response.headers.get('content-type') || '';
  return contentType.includes('application/json') ? response.json() : null;
}

/** GET /api/health/ — sin autenticación. */
export function getHealth() {
  return request('/api/health/');
}

/**
 * GET /api/users/me/ — requiere autenticación.
 * El backend todavía no tiene JWT configurado (ver Biblia del Proyecto,
 * sección 8): cuando lo tenga, aquí se añade el header Authorization.
 */
export function getCurrentUser(token) {
  return request('/api/users/me/', {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
}
