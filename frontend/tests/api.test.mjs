import test from 'node:test';
import assert from 'node:assert/strict';
import { getHealth, loginUser, registerUser, getCurrentUser } from '../src/services/api.js';

function mockFetch(callback) {
  const previous = globalThis.fetch;
  globalThis.fetch = callback;
  return () => { globalThis.fetch = previous; };
}

test('health usa la ruta pública esperada', async () => {
  let target;
  const restore = mockFetch(async (url) => { target = url; return Response.json({ status: 'ok' }); });
  try { assert.deepEqual(await getHealth(), { status: 'ok' }); assert.match(target, /\/api\/health\/$/); }
  finally { restore(); }
});

test('login envía usuario o email según el identificador', async () => {
  const requests = [];
  const restore = mockFetch(async (url, options) => {
    requests.push({ url, payload: JSON.parse(options.body) });
    return Response.json({ access: 'access-test', refresh: 'refresh-test' });
  });
  try {
    await loginUser('usuario', 'contrasena');
    await loginUser('alguien@example.com', 'contrasena');
    assert.deepEqual(requests[0].payload, { username: 'usuario', password: 'contrasena' });
    assert.deepEqual(requests[1].payload, { email: 'alguien@example.com', password: 'contrasena' });
    assert.ok(requests.every(({ url }) => url.endsWith('/api/users/login/')));
  } finally { restore(); }
});

test('getCurrentUser envía el token bearer al backend', async () => {
  let header;
  const restore = mockFetch(async (_url, options) => {
    header = options.headers.Authorization;
    return Response.json({ id: 1, username: 'demo', email: 'demo@example.com' });
  });
  try { await getCurrentUser('access-test'); assert.equal(header, 'Bearer access-test'); }
  finally { restore(); }
});

test('registro transmite los campos esperados', async () => {
  let payload;
  const restore = mockFetch(async (_url, options) => {
    payload = JSON.parse(options.body);
    return Response.json({ id: 42, username: 'demo', email: 'demo@example.com' }, { status: 201 });
  });
  try { await registerUser({ username: 'demo', email: 'demo@example.com', password: 'contrasena' }); assert.equal(payload.username, 'demo'); }
  finally { restore(); }
});

test('errores HTTP preservan status para el manejo de autenticación', async () => {
  const restore = mockFetch(async () => Response.json({detail:'Credenciales inválidas'}, {status: 401}));
  try { await assert.rejects(loginUser('usuario','mal'), error => error.status === 401 && /inválidas/.test(error.message)); }
  finally { restore(); }
});

test('fallo de red se devuelve con código NETWORK_ERROR', async () => {
  const restore = mockFetch(async () => { throw new TypeError('offline'); });
  try { await assert.rejects(getHealth(), error => error.code === 'NETWORK_ERROR'); }
  finally { restore(); }
});
