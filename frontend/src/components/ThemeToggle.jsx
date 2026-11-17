import { useTheme } from '../context/ThemeContext';
import Icon from './Icon';
export default function ThemeToggle() {const {theme,toggleTheme}=useTheme();return <button type="button" className="iconbtn" onClick={toggleTheme} aria-label={theme==='dark'?'Cambiar a tema claro':'Cambiar a tema oscuro'} title={theme==='dark'?'Tema claro':'Tema oscuro'}><Icon name={theme==='dark'?'sun':'moon'} size={19}/></button>}
