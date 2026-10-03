/**
 * Marca de KEFA AI: un nodo central (la IA) conectado a cuatro puntos
 * (los canales y servicios que orquesta). El trazo usa --ink y los puntos
 * usan --accent, así que cambia solo con el tema, sin props de color.
 */
export default function Logo({ size = 26 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      strokeWidth="1.6"
      aria-hidden="true"
    >
      <circle className="logo-ring" cx="12" cy="12" r="3" />
      <circle className="logo-dot" cx="4.5" cy="5" r="1.6" />
      <circle className="logo-dot" cx="19.5" cy="5" r="1.6" />
      <circle className="logo-dot" cx="4.5" cy="19" r="1.6" />
      <circle className="logo-dot" cx="19.5" cy="19" r="1.6" />
      <path
        className="logo-ring"
        d="M9.6 10.4 5.3 6.3M14.4 10.4l4.3-4.1M9.6 13.6l-4.3 4.1M14.4 13.6l4.3 4.1"
      />
    </svg>
  );
}
