/** Utilidades puras: dictado local de texto, sin permisos ni llamadas API. */
export function speechConstructor(browser) {
  return browser?.SpeechRecognition || browser?.webkitSpeechRecognition || null;
}

export function mergeDictation(existing, segment, maxLength = 2000) {
  const a = typeof existing === 'string' ? existing.trimEnd() : '';
  const b = typeof segment === 'string' ? segment.trim() : '';
  if (!b) return a.slice(0, maxLength);
  return `${a}${a ? ' ' : ''}${b}`.slice(0, maxLength);
}

export function speechErrorText(code) {
  return ({
    'not-allowed': 'Permite el uso del micrófono desde Chrome para poder dictar.',
    'service-not-allowed': 'El navegador no tiene permiso para reconocer la voz.',
    'audio-capture': 'No se encontró un micrófono disponible.',
    'network': 'El servicio de reconocimiento de voz no está disponible. Revisa tu conexión.',
    'language-not-supported': 'El reconocimiento en español de México no está disponible.',
    'no-speech': 'No escuché ninguna voz. Puedes volver a intentarlo.',
    'aborted': 'Se detuvo el dictado.',
  })[code] || 'No pude transcribir tu voz. Intenta de nuevo o escribe tu mensaje.';
}
