/**
 * Traducción del contrato Django al lenguaje del usuario final.
 * Nunca se anuncia éxito basándose únicamente en `accepted` de n8n.
 */
export const RESULT_LABELS = {
  processing: 'Pensando…',
  interrupted: 'Respuesta interrumpida',
  confirmation: 'Necesita autorización',
  prepared: 'Lista para continuar',
  sent: 'Enviada · por comprobar',
  rejected: 'No se pudo realizar',
  reported: 'Resultado comunicado',
  verified: 'Operación registrada',
  uncertain: 'Revisar resultado',
  error: 'Ocurrió un problema',
  cancelled: 'Cancelada',
  message: 'Respuesta del asistente',
  no_result: 'Sin respuesta',
};

export function actionInfo(tool) {
  if (tool === 'tasks.create' || tool?.startsWith('tasks.')) {
    return { kind: 'task', name: 'Tarea de Google Tasks', shortName: 'Tarea', icon: 'tasks', url: 'https://tasks.google.com/' };
  }
  if (tool === 'calendar.create_event' || tool?.startsWith('calendar.')) {
    return { kind: 'event', name: 'Evento de Google Calendar', shortName: 'Evento', icon: 'calendar', url: 'https://calendar.google.com/' };
  }
  return { kind: 'other', name: 'Solicitud', shortName: 'Acción', icon: 'sparkles', url: null };
}

export function isVerifiedExecution(result) {
  if (!result || !['succeeded', 'executed', 'completed', 'success'].includes(result.status)) return false;
  const data = result.execution_result || result.result || result.execution;
  return Boolean(data && typeof data === 'object' && (data.id || data.task_id || data.event_id));
}

export function normalizeAssistantResponse(payload) {
  const results = Array.isArray(payload?.resultados) ? payload.resultados.filter(Boolean) : [];
  const message = [payload?.respuesta, payload?.mensaje, payload?.message]
    .find(value => typeof value === 'string' && value.trim()) || '';

  if (results.some(result => result.decision === 'request_confirmation')) return { status: 'confirmation', results, message };
  if (results.some(result => ['failed', 'error'].includes(result.status))) return { status: 'error', results, message };
  if (results.some(result => result.decision === 'reject')) return { status: 'rejected', results, message };
  if (results.some(result => ['succeeded', 'executed', 'completed', 'success'].includes(result.status))) {
    const executed = results.filter(result => ['succeeded', 'executed', 'completed', 'success'].includes(result.status));
    return { status: executed.length > 0 && executed.every(isVerifiedExecution) ? 'verified' : 'reported', results, message };
  }
  if (results.some(result => ['accepted', 'queued', 'executing'].includes(result.status))) return { status: 'sent', results, message };
  if (results.some(result => result.status === 'prepared')) return { status: 'prepared', results, message };

  const responseText = results.find(result => result.decision === 'respond' && typeof result.message === 'string')?.message;
  if (responseText) return { status: 'message', results, message: responseText };
  if (message) return { status: 'message', results, message };
  return { status: 'no_result', results, message: '' };
}

export function describeResult(result) {
  const { name } = actionInfo(result?.tool);
  if (result?.decision === 'respond') return result.message || 'Aquí tienes mi respuesta.';
  if (result?.decision === 'request_confirmation') return `Para continuar con esta solicitud es necesaria una autorización adicional.`;
  if (result?.decision === 'reject') return result.reason || 'Esta acción no está disponible para tu cuenta.';
  if (result?.status === 'prepared') return `Entendí tu solicitud para ${name.toLowerCase()}. Aún no he realizado ningún cambio.`;
  if (['accepted', 'queued', 'executing'].includes(result?.status)) return `Tu solicitud para ${name.toLowerCase()} se envió. Abre el servicio para comprobar que se haya guardado.`;
  if (isVerifiedExecution(result)) return `El servicio devolvió un identificador para tu solicitud. Puedes revisarla en Google.`;
  if (['executed', 'succeeded', 'completed', 'success'].includes(result?.status)) return `Se informó el resultado de la solicitud, pero falta una confirmación verificable.`;
  return result?.reason || 'No se pudo determinar el resultado. Puedes revisar tu servicio conectado.';
}

/** Conserva la incertidumbre si el servidor no devolvió un resultado verificable. */
export function normalizeInstructionError(error, requestedExecution = false) {
  const normalized = normalizeAssistantResponse(error?.payload);
  const uncertain = requestedExecution && (error?.code === 'NETWORK_ERROR' || error?.status === 502 || error?.name === 'AbortError');
  return {
    status: uncertain ? 'uncertain' : 'error',
    error: error?.message || 'No fue posible completar la solicitud.',
    results: normalized.results,
    message: normalized.message,
  };
}
