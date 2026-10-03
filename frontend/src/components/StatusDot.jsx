import { useEffect, useState } from 'react';
import { getHealth } from '../services/api';

const LABELS = {
  checking: 'Comprobando conexión con el backend…',
  ok: 'Backend conectado',
  down: 'No se pudo contactar al backend',
};

export default function StatusDot() {
  const [status, setStatus] = useState('checking');

  useEffect(() => {
    let active = true;
    getHealth()
      .then(() => active && setStatus('ok'))
      .catch(() => active && setStatus('down'));
    return () => {
      active = false;
    };
  }, []);

  return (
    <span
      className={`status-dot status-dot--${status}`}
      role="status"
      aria-label={LABELS[status]}
      title={LABELS[status]}
    />
  );
}
