import { useEffect, useState } from 'react';
import { getHealth } from '../services/api';
const labels = {checking:'Comprobando conexión',ok:'API disponible',down:'API sin conexión'};
export default function StatusDot() {
  const [status,setStatus] = useState('checking');
  useEffect(() => { let mounted=true; getHealth().then(data => {if(mounted) setStatus(data?.status==='ok'?'ok':'down')}).catch(()=>{if(mounted)setStatus('down')}); return ()=>{mounted=false};},[]);
  return <span className="health-badge" role="status" title={labels[status]}><span className={`status-dot status-dot--${status}`}/><span className="health-label">{labels[status]}</span></span>;
}
