import test from 'node:test';
import assert from 'node:assert/strict';
import { speechConstructor, mergeDictation, speechErrorText } from '../src/services/speech.js';

test('reconocimiento detecta prefijo de Chrome y API estándar', () => {
  const fake = () => {};
  assert.equal(speechConstructor({ webkitSpeechRecognition: fake }), fake);
  assert.equal(speechConstructor({ SpeechRecognition: fake }), fake);
  assert.equal(speechConstructor({}), null);
});

test('dictado agrega texto sin borrar el mensaje y limita longitud', () => {
  assert.equal(mergeDictation('Agenda una reunión', 'mañana a las 5'), 'Agenda una reunión mañana a las 5');
  assert.equal(mergeDictation('', '  crea una tarea  '), 'crea una tarea');
  assert.equal(mergeDictation('Hola', 'mundo', 7), 'Hola mu');
  assert.equal(mergeDictation('Hola', ''), 'Hola');
});

test('errores de voz se explican al usuario sin códigos internos', () => {
  assert.match(speechErrorText('not-allowed'), /micrófono/);
  assert.match(speechErrorText('network'), /conexión/);
  assert.match(speechErrorText('unknown'), /No pude/);
});
