"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils/cn";

const ANCHO_DE_VENTANA = 2;

type Propiedades = {
  paginaActual: number;
  paginas: number;
  criterio: string;
};

export function Paginacion({ paginaActual, paginas, criterio }: Propiedades) {
  const pathname = usePathname();

  if (paginas <= 1) {
    return null;
  }

  function construirHref(pagina: number): string {
    const params = new URLSearchParams();
    if (criterio) {
      params.set("q", criterio);
    }
    if (pagina > 1) {
      params.set("page", String(pagina));
    }
    const consulta = params.toString();
    return consulta ? `${pathname}?${consulta}` : pathname;
  }

  const desde = Math.max(1, paginaActual - ANCHO_DE_VENTANA);
  const hasta = Math.min(paginas, paginaActual + ANCHO_DE_VENTANA);
  const paginasVisibles: number[] = [];
  for (let pagina = desde; pagina <= hasta; pagina += 1) {
    paginasVisibles.push(pagina);
  }

  return (
    <nav
      aria-label="Páginas del listado"
      className="flex flex-wrap items-center gap-x-3 gap-y-2 px-4 sm:px-0"
    >
      {paginaActual > 1 ? (
        <Link
          href={construirHref(paginaActual - 1)}
          className="inline-flex h-9 items-center rounded-[4px] px-2 text-[0.875rem] font-medium text-senal hover:bg-linea"
        >
          Anterior
        </Link>
      ) : null}

      <ul className="flex items-center gap-1">
        {paginasVisibles.map((pagina) => (
          <li key={pagina}>
            <Link
              href={construirHref(pagina)}
              aria-current={pagina === paginaActual ? "page" : undefined}
              className={cn(
                "inline-flex h-9 min-w-9 items-center justify-center rounded-[4px] px-2 text-[0.875rem] tabular-nums",
                pagina === paginaActual
                  ? "bg-tinta font-semibold text-papel"
                  : "text-senal hover:bg-linea",
              )}
            >
              {pagina}
            </Link>
          </li>
        ))}
      </ul>

      {paginaActual < paginas ? (
        <Link
          href={construirHref(paginaActual + 1)}
          className="inline-flex h-9 items-center rounded-[4px] px-2 text-[0.875rem] font-medium text-senal hover:bg-linea"
        >
          Siguiente
        </Link>
      ) : null}
    </nav>
  );
}
