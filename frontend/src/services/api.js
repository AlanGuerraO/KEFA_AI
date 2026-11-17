const API_URL = (import.meta.env?.VITE_API_URL || 'http://localhost:8080').replace(/\/$/, '');

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
    });
  } catch (cause) {
    if (cause?.name === 'AbortError') throw cause;
    const error = new Error('No se pudo conectar con KEFA AI. Comprueba tu conexión y que el backend esté activo.');
    error.code = 'NETWORK_ERROR';
    throw error;
  }

  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json')
    ? await response.json().catch(() => null)
    : null;

  if (!response.ok) {
    const message = payload?.error
      || payload?.message
      || payload?.detail
      || payload?.non_field_errors?.[0]
      || (response.status === 401 ? 'Usuario o contraseña incorrectos.' : null)
      || `La solicitud falló (${response.status}).`;
    const error = new Error(typeof message === 'string' ? message : 'Revisa los datos ingresados.');
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

export function getHealth() {
  return request('/api/health/');
}

export function loginUser(identifier, password) {
  const loginField = identifier.includes('@') ? 'email' : 'username';
  return request('/api/users/login/', {
    method: 'POST',
    body: JSON.stringify({ [loginField]: identifier, password }),
  });
}

export function registerUser({ username, email, password }) {
  return request('/api/users/register/', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  });
}

export function refreshToken(refresh) {
  return request('/api/users/token/refresh/', {
    method: 'POST',
    body: JSON.stringify({ refresh }),
  });
}

export function getCurrentUser(token) {
  return request('/api/users/me/', {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
}

/** API de orquestación actual: POST /api/ai/tool-calling/ */
export function sendInstruction(token, message, signal) {
  if (!token) throw new Error('Inicia sesión para enviar instrucciones.');
  return request('/api/ai/tool-calling/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ mensaje: message }),
    signal,
  });
}

/** La respuesta confirmar no ejecuta todavía en el backend actual (HTTP 501). */
export function respondToConfirmation(token, requestId, answer, signal) {
  if (!token) throw new Error('Inicia sesión para responder.');
  if (!['confirmar', 'rechazar', 'cancelar'].includes(answer)) {
    throw new Error('Respuesta de confirmación inválida.');
  }
  return request('/api/ai/confirmar-accion/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ request_id: requestId, respuesta: answer }),
    signal,
  });
}
