import { useCallback, useEffect, useRef, useState } from 'react';
import { mergeDictation, speechConstructor, speechErrorText } from '../services/speech';

/** Dictado de una frase en es-MX. Nunca envía mensajes ni ejecuta acciones. */
export function useVoiceDictation(onText) {
  const recognitionRef = useRef(null);
  const onTextRef = useRef(onText);
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState('');
  const [error, setError] = useState('');
  const [supported, setSupported] = useState(false);

  useEffect(() => { onTextRef.current = onText; }, [onText]);
  useEffect(() => { setSupported(Boolean(speechConstructor(window))); }, []);
  useEffect(() => () => {
    const instance = recognitionRef.current;
    if (instance) {
      instance.onresult = null;
      instance.onerror = null;
      instance.onend = null;
      instance.abort();
      recognitionRef.current = null;
    }
  }, []);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    // Esperar a onend para evitar enviar el formulario antes del resultado final.
  }, []);

  const start = useCallback(() => {
    const BrowserSpeech = speechConstructor(window);
    if (!BrowserSpeech) {
      setError('Tu navegador no admite el dictado. Prueba con Chrome actualizado.');
      return;
    }
    // No volver a iniciar si ya hay una sesión activa.
    if (recognitionRef.current) return;
    const recognition = new BrowserSpeech();
    recognition.lang = 'es-MX';
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.maxAlternatives = 1;
    const processed = new Set();
    recognition.onresult = event => {
      let interimText = '';
      for (let i = 0; i < event.results.length; i += 1) {
        const item = event.results[i];
        const transcript = item?.[0]?.transcript || '';
        if (item?.isFinal) {
          if (!processed.has(i)) {
            processed.add(i);
            if (transcript.trim()) onTextRef.current(previous => mergeDictation(previous, transcript));
          }
        } else interimText += `${transcript} `;
      }
      setInterim(interimText.trim());
    };
    recognition.onerror = event => {
      if (event.error !== 'aborted') setError(speechErrorText(event.error));
      setListening(false);
      setInterim('');
    };
    recognition.onend = () => {
      recognitionRef.current = null;
      setListening(false);
      setInterim('');
    };
    recognitionRef.current = recognition;
    setError('');
    setInterim('');
    try { recognition.start(); setListening(true); }
    catch { recognitionRef.current = null; setListening(false); setError('No se pudo iniciar el micrófono. Revisa los permisos del navegador.'); }
  }, []);

  return { supported, listening, interim, error, start, stop };
}
