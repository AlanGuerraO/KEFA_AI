import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { authenticate } = useAuth();
  const registered = Boolean(location.state?.registered);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    if (!username.trim() || !password) {
      setError('Ingresa tu usuario o correo y contraseña.');
      return;
    }
    setSubmitting(true);
    try {
      await authenticate(username, password);
      navigate(location.state?.from || '/dashboard', { replace: true });
    } catch (err) {
      setError(err.message || 'No se pudo iniciar sesión.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-marketing"><span className="auth-badge">ORGANIZA · CONECTA · AUTOMATIZA</span><span className="auth-marketing-orbit" aria-hidden="true"><Logo size={92}/></span><h2>Tu día, más claro.<br/><span>Tu tiempo, para ti.</span></h2><p>Un solo espacio para gestionar tus instrucciones, eventos y tareas. KEFA AI une tus herramientas, con control en cada paso.</p><span className="auth-marketing-foot">KEFA AI · Orquestador personal inteligente</span></div><div className="auth-card">
        <div className="brand"><Logo /><span className="brand-name">KEFA AI</span></div>
        <div className="auth-panel">
          <h1>Qué gusto verte de nuevo</h1>
          <p className="subtitle">Accede a tu espacio personal</p>
          {registered && <p className="success-message" role="status">Cuenta creada. Ya puedes iniciar sesión.</p>}
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="username">Usuario o correo electrónico</label>
              <input id="username" name="username" autoComplete="username" required
                placeholder="Tu usuario o correo" value={username}
                onChange={(event) => setUsername(event.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="password">Contraseña</label>
              <input id="password" name="password" type="password" autoComplete="current-password"
                required placeholder="Tu contraseña" value={password}
                onChange={(event) => setPassword(event.target.value)} />
            </div>
            {error && <p className="field-error" role="alert">{error}</p>}
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Iniciando sesión…' : 'Iniciar sesión'}
            </button>
          </form>
          <div className="auth-links auth-links--center">
            <span>¿Aún no tienes cuenta?</span>
            <Link to="/registro">Crear cuenta</Link>
          </div>
          <p className="auth-note">La recuperación de contraseña estará disponible cuando exista un flujo de recuperación en el backend.</p>
        </div>
      </div>
    </div>
  );
}
