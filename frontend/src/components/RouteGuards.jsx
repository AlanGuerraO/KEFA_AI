import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function RequireAuth() {
  const { status } = useAuth();
  const location = useLocation();
  if (status === 'checking') {
    return <main className="route-loading" role="status">Comprobando sesión…</main>;
  }
  if (status !== 'authenticated') {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <Outlet />;
}

export function GuestOnly() {
  const { status } = useAuth();
  if (status === 'checking') {
    return <main className="route-loading" role="status">Comprobando sesión…</main>;
  }
  return status === 'authenticated'
    ? <Navigate to="/dashboard" replace />
    : <Outlet />;
}
