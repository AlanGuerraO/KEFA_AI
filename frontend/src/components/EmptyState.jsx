import Icon from './Icon';
export default function EmptyState({icon='clock',title,description,actions}) {return <div className="empty-state"><span className="empty-illustration"><Icon name={icon} size={27}/></span><h3>{title}</h3><p>{description}</p>{actions&&<div className="empty-actions">{actions}</div>}</div>}
