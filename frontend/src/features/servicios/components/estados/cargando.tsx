export function Cargando() {
  return (
    <div
      role="status"
      aria-live="polite"
      className="overflow-hidden rounded-lg border border-panel-borde bg-panel-superficie"
    >
      <p className="border-b border-panel-borde px-4 py-3 text-sm text-panel-secundario">
        Cargando servicios…
      </p>
      <ul aria-hidden="true" className="divide-y divide-panel-borde">
        {Array.from({ length: 5 }, (_, indice) => (
          <li
            key={indice}
            className="flex flex-col gap-2 px-4 py-5 sm:flex-row sm:items-center sm:gap-6"
          >
            <span className="h-4 w-40 max-w-full rounded bg-panel-suave" />
            <span className="h-4 w-32 max-w-full rounded bg-panel-suave" />
            <span className="h-4 w-24 max-w-full rounded bg-panel-suave" />
            <span className="h-4 w-20 max-w-full rounded bg-panel-suave" />
          </li>
        ))}
      </ul>
    </div>
  );
}
