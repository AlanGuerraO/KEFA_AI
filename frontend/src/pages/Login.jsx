import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  function handleSubmit(event) {
    event.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Ingresa tu correo y tu contraseña.');
      return;
    }

    // TODO(backend): cuando el backend exponga el endpoint de login con JWT
    // (ver Biblia del Proyecto, sección 8 — pendiente de proveedor/implementación),
    // aquí se hace el POST real y se guarda el token antes de navegar.
    setSubmitting(true);
    navigate('/dashboard');
  }

  return (
    <div className="auth-screen">
      <div className="auth-card">
        <div className="brand">
          <Logo />
          <span className="brand-name">KEFA AI</span>
        </div>

        <div className="auth-panel">
          <h1>Bienvenida de nuevo</h1>
          <p className="subtitle">Inicia sesión en tu espacio KEFA AI</p>

          <form onSubmit={handleSubmit} noValidate>
            <div className="field">
              <label htmlFor="email">Correo electrónico</label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="correo@ejemplo.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </div>

            <div className="field">
              <label htmlFor="password">Contraseña</label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                placeholder="Tu contraseña"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>

            {error && (
              <p className="field-error" role="alert">
                {error}
              </p>
            )}

            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Iniciando sesión…' : 'Iniciar sesión'}
            </button>
          </form>

          <div className="auth-links">
            <a href="#">¿Olvidaste tu contraseña?</a>
            <a href="#">Crear cuenta</a>
          </div>
        </div>
      </div>
    </div>
  );
}
