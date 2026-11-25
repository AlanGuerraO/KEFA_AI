import { Fragment } from 'react';

/** Formato seguro, sin HTML crudo ni dependencias extra. */
function inline(text) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((piece, index) =>
    piece.startsWith('**') && piece.endsWith('**')
      ? <strong key={index}>{piece.slice(2, -2)}</strong>
      : <Fragment key={index}>{piece}</Fragment>
  );
}

export default function AssistantFormattedText({ text }) {
  if (!text || typeof text !== 'string') return null;
  const lines = text.split(/\r?\n/);
  const output = [];
  let list = [];
  function flush() {
    if (list.length) {
      output.push(<ul key={`list-${output.length}`} className="kefa-answer-list">{list.map((t, i) => <li key={i}>{inline(t)}</li>)}</ul>);
      list = [];
    }
  }
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i].trim();
    const isList = line.match(/^(?:[-•*]|\d+[.)])\s+(.+)$/);
    if (isList) { list.push(isList[1]); continue; }
    flush();
    if (!line) continue;
    output.push(<p key={`p-${i}`} className="kefa-answer-paragraph">{inline(line.replace(/^#{1,4}\s*/, ''))}</p>);
  }
  flush();
  return <div className="kefa-answer-content">{output}</div>;
}
