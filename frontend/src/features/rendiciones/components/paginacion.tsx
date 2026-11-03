"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const ANCHO_DE_VENTANA = 2;

export function PaginacionRendiciones({
  paginaActual,
  paginas,
  criterio,
}: {
  paginaActual: number;
  paginas: number;
  criterio: string;
}) {
  const pathname = usePathname();

  if (paginas <= 1) {
    return null;
  }

  function construirHref(pagina: number): string {
    const parametros = new URLSearchParams();
    if (criterio) {
      parametros.set("q", criterio);
    }
    if (pagina > 1) {
      parametros.set("page", String(pagina));
    }
    const consulta = parametros.toString();
    return consulta ? `${pathname}?${consulta}` : pathname;
  }

  const desde = Math.max(1, paginaActual - ANCHO_DE_VENTANA);
  const hasta = Math.min(paginas, paginaActual + ANCHO_DE_VENTANA);
  const visibles = Array.from(
    { length: hasta - desde + 1 },
    (_, indice) => desde + indice,
  );

  return (
    <nav
      aria-label="Páginas del listado de rendiciones"
      className="flex flex-wrap items-center gap-1"
    >
      {paginaActual > 1 ? (
        <Link
          href={construirHref(paginaActual - 1)}
          className="inline-flex h-9 items-center rounded-md px-3 text-sm font-medium text-[#62738a] hover:bg-[#f3f5f8] dark:text-[#94a3b8] dark:hover:bg-[#18263d]"
        >
          Anterior
        </Link>
      ) : null}
      <ul className="flex items-center gap-1">
        {visibles.map((pagina) => (
          <li key={pagina}>
            <Link
              href={construirHref(pagina)}
              aria-current={pagina === paginaActual ? "page" : undefined}
              className={`inline-flex h-9 min-w-9 items-center justify-center rounded-md px-2 text-sm tabular-nums ${
                pagina === paginaActual
                  ? "bg-[#2165d5] font-semibold text-white dark:bg-[#2563eb]"
                  : "text-[#62738a] hover:bg-[#f3f5f8] dark:text-[#94a3b8] dark:hover:bg-[#18263d]"
              }`}
            >
              {pagina}
            </Link>
          </li>
        ))}
      </ul>
      {paginaActual < paginas ? (
        <Link
          href={construirHref(paginaActual + 1)}
          className="inline-flex h-9 items-center rounded-md px-3 text-sm font-medium text-[#62738a] hover:bg-[#f3f5f8] dark:text-[#94a3b8] dark:hover:bg-[#18263d]"
        >
          Siguiente
        </Link>
      ) : null}
    </nav>
  );
}
