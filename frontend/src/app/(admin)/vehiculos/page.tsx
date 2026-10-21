import Link from "next/link";
import { Suspense } from "react";

import { BuscadorVehiculos } from "@/features/vehiculos/components/buscador-vehiculos";
import { CabeceraListado } from "@/features/vehiculos/components/cabecera-listado";
import { Cargando } from "@/features/vehiculos/components/estados/cargando";
import { EstadoError } from "@/features/vehiculos/components/estados/error";
import { EstadoVacio } from "@/features/vehiculos/components/estados/vacio";
import { ListadoVehiculos } from "@/features/vehiculos/components/listado-vehiculos";
import { Paginacion } from "@/features/vehiculos/components/paginacion";
import { listarVehiculos, TAMANO_DE_PAGINA } from "@/lib/api/vehiculos";
import { ErrorApi } from "@/lib/api/http";
import { cn } from "@/lib/utils/cn";
import {
  primeraFilaDeLaPagina,
  totalPaginas,
  ultimaFilaDeLaPagina,
} from "@/lib/utils/formato";

type SearchParams = PageProps<"/vehiculos">["searchParams"];

export const metadata = {
  title: "Vehículos",
};

const RUTAS = [
  { href: "/", etiqueta: "Clientes" },
  { href: "/choferes", etiqueta: "Choferes" },
  { href: "/vehiculos", etiqueta: "Vehículos" },
];

export default function PaginaVehiculos({ searchParams }: PageProps<"/vehiculos">) {
  return (
    <>
      <header className="banda bg-tinta text-papel">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-5 px-4 py-6 sm:px-6">
          <p className="text-[0.8125rem] font-medium text-papel/70">
            Fletes y Mudanzas Express
          </p>
          <nav aria-label="Secciones" className="flex flex-wrap gap-x-5 gap-y-2">
            {RUTAS.map((ruta) => (
              <Link
                key={ruta.href}
                href={ruta.href}
                aria-current={ruta.href === "/vehiculos" ? "page" : undefined}
                className={cn(
                  "text-[0.9375rem] font-medium",
                  ruta.href === "/vehiculos"
                    ? "text-papel underline decoration-2 underline-offset-8"
                    : "text-papel/65 hover:text-papel",
                )}
              >
                {ruta.etiqueta}
              </Link>
            ))}
          </nav>
          <Suspense fallback={<div className="h-10 w-full max-w-sm" />}>
            <BuscadorConCriterio searchParams={searchParams} />
          </Suspense>
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl py-8 sm:px-6">
        <Suspense fallback={<Cargando />}>
          <Listado searchParams={searchParams} />
        </Suspense>
      </main>
    </>
  );
}

async function BuscadorConCriterio({ searchParams }: { searchParams: SearchParams }) {
  const criterio = leerTexto(await searchParams, "q");
  return <BuscadorVehiculos criterioInicial={criterio} />;
}

async function Listado({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const criterio = leerTexto(params, "q");
  const pagina = leerNumero(params, "page");

  let resultado;
  try {
    resultado = await listarVehiculos({
      q: criterio || undefined,
      page: pagina,
      size: TAMANO_DE_PAGINA,
    });
  } catch (error) {
    if (error instanceof ErrorApi) {
      return <EstadoError clase={error.clase} />;
    }
    throw error;
  }

  const paginas = totalPaginas(resultado.total, TAMANO_DE_PAGINA);

  if (resultado.items.length === 0) {
    if (criterio || resultado.total === 0) {
      return <EstadoVacio criterio={criterio} rutaSinBusqueda="/vehiculos" />;
    }
    return <PaginaFueraDeRango pagina={pagina} />;
  }

  return (
    <div className="flex flex-col gap-6">
      <CabeceraListado total={resultado.total} paginas={paginas} />
      <ListadoVehiculos vehiculos={resultado.items} />

      <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-3 px-4 sm:px-0">
        <Paginacion paginaActual={resultado.page} paginas={paginas} criterio={criterio} />
        <p className="text-[0.8125rem] text-tinta-media tabular-nums">
          {`Mostrando ${primeraFilaDeLaPagina(resultado.page, TAMANO_DE_PAGINA)}–${ultimaFilaDeLaPagina(
            resultado.page,
            TAMANO_DE_PAGINA,
            resultado.total,
          )} de ${resultado.total}`}
        </p>
      </div>
    </div>
  );
}

function PaginaFueraDeRango({ pagina }: { pagina: number }) {
  return (
    <div role="status" className="border-t border-linea px-4 py-12 sm:px-0">
      <p className="text-[1rem] font-semibold text-tinta">
        La página {pagina} no tiene vehículos.
      </p>
      <p className="mt-2 text-[0.875rem] text-tinta-media">
        El listado no llega tan lejos. Volvé a empezar desde el principio.
      </p>
      <Link
        href="/vehiculos"
        className="mt-5 inline-block rounded-[4px] border border-linea bg-white px-4 py-2 text-[0.875rem] font-medium text-senal hover:border-senal"
      >
        Ir a la primera página
      </Link>
    </div>
  );
}

function leerTexto(
  params: Record<string, string | string[] | undefined>,
  clave: string,
): string {
  const valor = params[clave];
  return typeof valor === "string" ? valor.trim() : "";
}

function leerNumero(
  params: Record<string, string | string[] | undefined>,
  clave: string,
): number {
  const valor = leerTexto(params, clave);
  if (!/^\d+$/.test(valor)) {
    return 1;
  }
  return Math.max(1, Number.parseInt(valor, 10));
}
