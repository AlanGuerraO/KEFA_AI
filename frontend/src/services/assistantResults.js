/**
 * Adapta las respuestas actuales de Django a estados de UI. Nunca equipara
 * 'prepared' o 'accepted' con una acción ejecutada en Google.
 */
export function normalizeAssistantResponse(payload) {
  const results = Array.isArray(payload?.resultados) ? payload.resultados.filter(Boolean) : [];
  const message = [payload?.respuesta, payload?.mensaje, payload?.message]
    .find(value => typeof value === 'string' && value.trim()) || '';

  if (results.some(result => result.decision === 'request_confirmation')) {
    return { status: 'confirmation', results, message };
  }
  if (results.some(result => ['failed', 'error'].includes(result.status))) {
    return { status: 'error', results, message };
  }
  if (results.some(result => result.decision === 'reject')) {
    return { status: 'rejected', results, message };
  }
  if (results.some(result => ['succeeded', 'executed', 'completed', 'success'].includes(result.status))) {
    return { status: 'reported', results, message };
  }
  if (results.some(result => ['prepared', 'accepted', 'queued', 'executing'].includes(result.status))) {
    return { status: 'prepared', results, message };
  }
  if (message) return { status: 'message', results, message };
  return { status: 'no_result', results, message: '' };
}

export const RESULT_LABELS = {
  processing: 'Procesando',
  interrupted: 'Sin respuesta confirmada',
  confirmation: 'Requiere confirmación',
  prepared: 'Preparada, no ejecutada',
  rejected: 'Solicitud rechazada',
  reported: 'Resultado informado por el servidor',
  error: 'Error',
  cancelled: 'Cancelada',
  message: 'Respuesta recibida',
  no_result: 'Sin acción reconocida',
};

export function isVerifiedExecution(result) {
  if (!result || !['succeeded', 'executed', 'completed', 'success'].includes(result.status)) return false;
  const data = result.execution_result || result.result || result.execution;
  return Boolean(data && typeof data === 'object' && (data.id || data.task_id || data.event_id));
}

export function describeResult(result) {
  if (result?.decision === 'request_confirmation') {
    return 'Esta herramienta requiere tu autorización. No se ha ejecutado.';
  }
  if (result?.decision === 'reject') return result.reason || 'El servidor rechazó la herramienta.';
  if (result?.status === 'prepared') return 'El orquestador validó y preparó esta herramienta. Aún no se ha ejecutado en n8n.';
  if (['accepted', 'queued', 'executing'].includes(result?.status)) return 'Solicitud recibida para procesamiento. No se ha comprobado el resultado externo.';
  if (isVerifiedExecution(result)) return 'El servidor devolvió un resultado con identificador de ejecución.';
  if (['executed', 'succeeded', 'completed', 'success'].includes(result?.status)) return 'El servidor informó una ejecución, pero no devolvió un identificador externo verificable.';
  return result?.reason || 'Consulta el estado de la operación en el backend.';
}
