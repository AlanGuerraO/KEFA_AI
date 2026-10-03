import { Navigate, Route, Routes } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Placeholder from './pages/Placeholder';

export default function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        {/* TODO(backend): envolver estas rutas en un guard de autenticación
            real una vez que el backend tenga JWT (ver Biblia del Proyecto,
            sección 8). Por ahora son de libre acceso para poder maquetar. */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/conversaciones" element={<Placeholder title="Conversaciones" />} />
        <Route path="/configuracion" element={<Placeholder title="Configuración" />} />
        <Route path="/cuenta" element={<Placeholder title="Mi cuenta" />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </ThemeProvider>
  );
}
