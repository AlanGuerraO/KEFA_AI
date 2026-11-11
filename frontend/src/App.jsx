import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { GuestOnly, RequireAuth } from './components/RouteGuards';
import AppLayout from './components/AppLayout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Conversations from './pages/Conversations';
import Activity from './pages/Activity';
import Integrations from './pages/Integrations';
import Settings from './pages/Settings';
import Account from './pages/Account';
export default function App() {
  return <ThemeProvider><AuthProvider><Routes>
    <Route element={<GuestOnly />}><Route path="/login" element={<Login/>} /><Route path="/registro" element={<Register/>} /></Route>
    <Route element={<RequireAuth />}><Route element={<AppLayout />}>
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/conversaciones" element={<Conversations />} />
      <Route path="/actividad" element={<Activity />} />
      <Route path="/integraciones" element={<Integrations />} />
      <Route path="/configuracion" element={<Settings />} />
      <Route path="/cuenta" element={<Account />} />
    </Route></Route>
    <Route path="/" element={<Navigate to="/dashboard" replace />} />
    <Route path="*" element={<Navigate to="/dashboard" replace />} />
  </Routes></AuthProvider></ThemeProvider>;
}
