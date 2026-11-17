import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';
import { registerUser } from '../services/api';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  function update(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    if (form.password !== form.confirmPassword) {
      setError('Las contraseñas no coinciden.');
      return;
    }
    setSubmitting(true);
    try {
      await registerUser({ username: form.username.trim(), email: form.email.trim(), password: form.password });
      navigate('/login', { replace: true, state: { registered: true } });
    } catch (err) {
      const payload = err.payload;
      const details = payload && typeof payload === 'object'
        ? Object.entries(payload).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(' ') : value}`).join(' ')
        : '';
      setError(details || err.message || 'No se pudo crear la cuenta.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-marketing"><span className="auth-badge">TU ESPACIO PERSONAL</span><span className="auth-marketing-orbit" aria-hidden="true"><Logo size={92}/></span><h2>Menos pasos.<br/><span>Más posibilidades.</span></h2><p>Crea tu cuenta y construye un espacio donde tus herramientas trabajen juntas, siempre con tu autorización.</p><span className="auth-marketing-foot">KEFA AI · Orquestador personal inteligente</span></div><div className="auth-card">
        <div className="brand"><Logo /><span className="brand-name">KEFA AI</span></div>
        <div className="auth-panel">
          <h1>Crear cuenta</h1>
          <p className="subtitle">Empieza a organizarte desde un solo lugar</p>
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="username">Nombre de usuario</label>
              <input id="username" name="username" autoComplete="username" required minLength={3}
                value={form.username} onChange={update} />
            </div>
            <div className="field">
              <label htmlFor="email">Correo electrónico</label>
              <input id="email" name="email" type="email" autoComplete="email" required
                value={form.email} onChange={update} />
            </div>
            <div className="field">
              <label htmlFor="password">Contraseña</label>
              <input id="password" name="password" type="password" autoComplete="new-password" required
                minLength={8} value={form.password} onChange={update} />
            </div>
            <div className="field">
              <label htmlFor="confirmPassword">Confirmar contraseña</label>
              <input id="confirmPassword" name="confirmPassword" type="password" autoComplete="new-password"
                required value={form.confirmPassword} onChange={update} />
            </div>
            {error && <p className="field-error" role="alert">{error}</p>}
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Creando cuenta…' : 'Crear cuenta'}
            </button>
          </form>
          <div className="auth-links auth-links--center">
            <span>¿Ya tienes cuenta?</span><Link to="/login">Iniciar sesión</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
