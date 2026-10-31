"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils/cn";

const ANCHO_DE_VENTANA = 2;

export function Paginacion({
  paginaActual,
  paginas,
}: {
  paginaActual: number;
  paginas: number;
}) {
  const pathname = usePathname();
  if (paginas <= 1) {
    return null;
  }

  function hrefDePagina(pagina: number): string {
    return pagina > 1 ? `${pathname}?page=${pagina}` : pathname;
  }

  const desde = Math.max(1, paginaActual - ANCHO_DE_VENTANA);
  const hasta = Math.min(paginas, paginaActual + ANCHO_DE_VENTANA);
  const visibles = Array.from(
    { length: hasta - desde + 1 },
    (_, indice) => desde + indice,
  );

  return (
    <nav
      aria-label="Páginas del listado"
      className="flex flex-wrap items-center gap-x-1 gap-y-2"
    >
      {paginaActual > 1 ? (
        <Link
          href={hrefDePagina(paginaActual - 1)}
          className="inline-flex h-9 items-center rounded-md px-3 text-sm font-medium text-panel-secundario hover:bg-panel-suave"
        >
          Anterior
        </Link>
      ) : null}
      <ul className="flex items-center gap-1">
        {visibles.map((pagina) => (
          <li key={pagina}>
            <Link
              href={hrefDePagina(pagina)}
              aria-current={pagina === paginaActual ? "page" : undefined}
              className={cn(
                "inline-flex h-9 min-w-9 items-center justify-center rounded-md px-2 text-sm tabular-nums",
                pagina === paginaActual
                  ? "bg-panel-primario font-semibold text-white"
                  : "text-panel-secundario hover:bg-panel-suave",
              )}
            >
              {pagina}
            </Link>
          </li>
        ))}
      </ul>
      {paginaActual < paginas ? (
        <Link
          href={hrefDePagina(paginaActual + 1)}
          className="inline-flex h-9 items-center rounded-md px-3 text-sm font-medium text-panel-secundario hover:bg-panel-suave"
        >
          Siguiente
        </Link>
      ) : null}
    </nav>
  );
}
