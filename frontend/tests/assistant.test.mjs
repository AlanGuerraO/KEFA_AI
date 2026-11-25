import test from 'node:test';
import assert from 'node:assert/strict';
import { sendInstruction, respondToConfirmation } from '../src/services/api.js';
import { normalizeAssistantResponse, normalizeInstructionError, describeResult, isVerifiedExecution, actionInfo, RESULT_LABELS } from '../src/services/assistantResults.js';

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
    assert.deepEqual(JSON.parse(received.options.body), { mensaje: 'Crea una tarea', ejecutar: false });
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
  assert.match(describeResult(response.results[0]), /Aún no he realizado ningún cambio/);
});

test('diferencia confirmación, rechazo, respuesta texto y respuesta sin herramientas', () => {
  assert.equal(normalizeAssistantResponse({ resultados: [{ decision: 'request_confirmation', request_id: 'sol-1' }] }).status, 'confirmation');
  assert.equal(normalizeAssistantResponse({ resultados: [{ decision: 'reject', reason: 'Sin permisos' }] }).status, 'rejected');
  assert.equal(normalizeAssistantResponse({ mensaje: 'Hola' }).status, 'message');
  assert.equal(normalizeAssistantResponse({ resultados: [] }).status, 'no_result');
});

test('no considera HTTP aceptado como operación completada', () => {
  const normalized = normalizeAssistantResponse({ resultados: [{ decision: 'execute', status: 'accepted' }] });
  assert.equal(normalized.status, 'sent');
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


test('el envío de ejecución opt-in incluye ejecutar=true y no agrega permisos desde la web', async () => {
  let payload;
  await withFetch(async (_url, options) => {
    payload = JSON.parse(options.body);
    return Response.json({ resultados: [{ decision: 'execute', tool: 'tasks.create', status: 'accepted', http_status: 200 }] });
  }, async () => {
    const response = await sendInstruction('jwt', '  Crea una tarea  ', { execute: true });
    assert.deepEqual(payload, { mensaje: 'Crea una tarea', ejecutar: true });
    assert.equal(normalizeAssistantResponse(response).status, 'sent');
    assert.ok(!Object.hasOwn(payload, 'granted_permissions'));
  });
});

test('no se permite enviar ejecución con un modo inválido o texto vacío', () => {
  assert.throws(() => sendInstruction('jwt', '', { execute: true }), /Escribe una instrucción/);
  assert.throws(() => sendInstruction('jwt', 'hola', { execute: 'true' }), /booleano/);
  assert.throws(() => sendInstruction('jwt', 'x'.repeat(2001)), /máximo 2000/);
});

test('el resultado con identificador externo distingue verificado e informado', () => {
  const success = normalizeAssistantResponse({ resultados: [{ decision: 'execute', tool: 'tasks.create', status: 'succeeded', execution_result: { id: 't-12' } }] });
  assert.equal(success.status, 'verified');
  const uncertain = normalizeAssistantResponse({ resultados: [{ decision: 'execute', tool: 'tasks.create', status: 'succeeded' }] });
  assert.equal(uncertain.status, 'reported');
});

test('errores 409 conservan las decisiones sin fingir una ejecución', async () => {
  await withFetch(async () => Response.json({ error: 'Se requiere una única acción.', resultados: [{ decision: 'reject', tool: 'tasks.create', status: 'rejected', reason: 'Sin permisos' }] }, { status: 409 }), async () => {
    await assert.rejects(sendInstruction('jwt', 'Crea tarea', { execute: true }), error => {
      const state = normalizeInstructionError(error, true);
      assert.equal(state.status, 'error');
      assert.equal(state.results[0].reason, 'Sin permisos');
      return true;
    });
  });
});

test('una desconexión durante ejecución se identifica como incierta, sin reintentar', () => {
  const error = Object.assign(new Error('Sin conexión'), { code: 'NETWORK_ERROR' });
  assert.equal(normalizeInstructionError(error, true).status, 'uncertain');
  assert.equal(normalizeInstructionError(error, false).status, 'error');
  assert.equal(normalizeInstructionError(Object.assign(new Error('502'), { status: 502 }), true).status, 'uncertain');
  assert.equal(normalizeInstructionError(Object.assign(new Error('Servidor sin ejecutar'), { status: 503 }), true).status, 'error');
});


test('Gemini puede responder aclaraciones sin generar una herramienta ejecutable', () => {
  const result = normalizeAssistantResponse({resultados: [
    {decision: 'respond', status: 'response', message: '¿A qué hora termina la reunión?'}
  ]});
  assert.equal(result.status, 'message');
  assert.equal(result.message, '¿A qué hora termina la reunión?');
});


test('estado enviado se distingue del análisis y no afirma que la tarea existe', () => {
  const prepared = normalizeAssistantResponse({ resultados: [{ decision: 'execute', tool: 'tasks.create', status: 'prepared' }] });
  const sent = normalizeAssistantResponse({ resultados: [{ decision: 'execute', tool: 'tasks.create', status: 'accepted' }] });
  assert.equal(prepared.status, 'prepared');
  assert.equal(sent.status, 'sent');
  assert.match(RESULT_LABELS[sent.status], /por comprobar/);
  assert.match(describeResult(sent.results[0]), /comprobar/);
});

test('presenta nombres y enlaces amigables para usuario final', () => {
  assert.equal(actionInfo('tasks.create').name, 'Tarea de Google Tasks');
  assert.match(actionInfo('tasks.create').url, /tasks.google.com/);
  assert.equal(actionInfo('calendar.create_event').name, 'Evento de Google Calendar');
  assert.match(actionInfo('calendar.create_event').url, /calendar.google.com/);
  assert.equal(actionInfo('unknown').url, null);
});

test('no interpreta una respuesta de Gemini como acción realizada', () => {
  const result = normalizeAssistantResponse({ resultados: [{ decision:'respond', status:'response', message:'Claro, ¿para qué fecha?' }] });
  assert.equal(result.status, 'message');
  assert.equal(result.message, 'Claro, ¿para qué fecha?');
});

test('modo automático envía ejecutar=true para preguntas y órdenes, sin confirmación del frontend', async () => {
  const { sendAutomaticInstruction } = await import('../src/services/api.js');
  const payloads = [];
  await withFetch(async (_url, options) => {
    payloads.push(JSON.parse(options.body));
    return Response.json({ resultados: [{ decision: 'respond', status: 'response', message: 'Te puedo ayudar.' }] });
  }, async () => {
    await sendAutomaticInstruction('jwt-demo', '¿Cómo organizo mis pendientes?');
    await sendAutomaticInstruction('jwt-demo', 'Crea una tarea llamada Exposición');
  });
  assert.deepEqual(payloads, [
    { mensaje: '¿Cómo organizo mis pendientes?', ejecutar: true },
    { mensaje: 'Crea una tarea llamada Exposición', ejecutar: true },
  ]);
  assert.ok(payloads.every(p => !Object.hasOwn(p, 'confirmed')));
});
