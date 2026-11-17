import test from 'node:test';
import assert from 'node:assert/strict';
import { sendInstruction, respondToConfirmation } from '../src/services/api.js';
import { normalizeAssistantResponse, describeResult, isVerifiedExecution } from '../src/services/assistantResults.js';

function withFetch(mock, callback) {
  const previous = globalThis.fetch;
  globalThis.fetch = mock;
  return Promise.resolve().then(callback).finally(() => { globalThis.fetch = previous; });
}

test('envía instrucción al endpoint de IA con JWT y campo mensaje', async () => {
  let received;
  await withFetch(async (url, options) => {
    received = { url, options };
    return Response.json({ resultados: [{ decision: 'execute', tool: 'tasks.create', status: 'prepared' }] });
  }, async () => {
    const response = await sendInstruction('jwt-demo', 'Crea una tarea');
    assert.equal(response.resultados[0].status, 'prepared');
    assert.match(received.url, /\/api\/ai\/tool-calling\/$/);
    assert.equal(received.options.method, 'POST');
    assert.equal(received.options.headers.Authorization, 'Bearer jwt-demo');
    assert.deepEqual(JSON.parse(received.options.body), { mensaje: 'Crea una tarea' });
  });
});

test('envía confirmación vinculada a request_id y no un confirmed=true', async () => {
  let body, url;
  await withFetch(async (target, options) => {
    url = target; body = JSON.parse(options.body);
    return Response.json({ status: 'cancelled', request_id: 'sol-456' });
  }, async () => {
    assert.deepEqual(await respondToConfirmation('token', 'sol-456', 'cancelar'), { status: 'cancelled', request_id: 'sol-456' });
    assert.match(url, /\/api\/ai\/confirmar-accion\/$/);
    assert.deepEqual(body, { request_id: 'sol-456', respuesta: 'cancelar' });
    assert.ok(!Object.hasOwn(body, 'confirmed'));
  });
});

test('muestra el mensaje del backend ante HTTP 501 sin fingir ejecución', async () => {
  await withFetch(async () => Response.json({ error: 'La confirmación aún no está habilitada.' }, { status: 501 }), async () => {
    await assert.rejects(respondToConfirmation('token', 'sol-456', 'confirmar'), error => error.status === 501 && /no está habilitada/.test(error.message));
  });
});

test('no permite respuestas de confirmación fuera del contrato', async () => {
  assert.throws(() => respondToConfirmation('jwt', 'sol-456', 'si'), /inválida/);
});

test('normaliza preparada como pendiente de ejecución', () => {
  const response = normalizeAssistantResponse({ resultados: [{ decision: 'execute', tool: 'tasks.create', status: 'prepared' }] });
  assert.equal(response.status, 'prepared');
  assert.match(describeResult(response.results[0]), /Aún no se ha ejecutado/);
});

test('diferencia confirmación, rechazo, respuesta texto y respuesta sin herramientas', () => {
  assert.equal(normalizeAssistantResponse({ resultados: [{ decision: 'request_confirmation', request_id: 'sol-1' }] }).status, 'confirmation');
  assert.equal(normalizeAssistantResponse({ resultados: [{ decision: 'reject', reason: 'Sin permisos' }] }).status, 'rejected');
  assert.equal(normalizeAssistantResponse({ mensaje: 'Hola' }).status, 'message');
  assert.equal(normalizeAssistantResponse({ resultados: [] }).status, 'no_result');
});

test('no considera HTTP aceptado como operación completada', () => {
  const normalized = normalizeAssistantResponse({ resultados: [{ decision: 'execute', status: 'accepted' }] });
  assert.equal(normalized.status, 'prepared');
  assert.equal(isVerifiedExecution(normalized.results[0]), false);
});

test('solo acepta identificador externo como prueba de resultado reportado', () => {
  assert.equal(isVerifiedExecution({ status: 'succeeded' }), false);
  assert.equal(isVerifiedExecution({ status: 'succeeded', execution_result: { id: 'abc-123' } }), true);
  assert.equal(isVerifiedExecution({ status: 'prepared', execution_result: { id: 'abc-123' } }), false);
});

test('no envía información si falta sesión', async () => {
  assert.throws(() => sendInstruction('', 'Crea tarea'), /Inicia sesión/);
});
