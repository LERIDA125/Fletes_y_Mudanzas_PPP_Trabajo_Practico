export function Cargando() {
  return (
    <div role="status" aria-live="polite" className="border-t border-linea">
      <p className="px-4 py-3 text-[0.875rem] text-tinta-media sm:px-0">
        Cargando servicios…
      </p>
      <ul aria-hidden="true">
        {Array.from({ length: 5 }, (_, indice) => (
          <li
            key={indice}
            className="flex flex-col gap-2 border-t border-linea px-4 py-5 sm:flex-row sm:items-center sm:gap-6 sm:px-0"
          >
            <span className="h-4 w-40 bg-linea" />
            <span className="h-4 w-32 max-w-full bg-linea" />
            <span className="h-4 w-24 bg-linea" />
            <span className="h-4 w-20 bg-linea" />
          </li>
        ))}
      </ul>
    </div>
  );
}
