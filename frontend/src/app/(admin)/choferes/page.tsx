import Link from "next/link";
import { Suspense } from "react";

import { BuscadorChoferes } from "@/features/choferes/components/buscador-choferes";
import { CabeceraListado } from "@/features/choferes/components/cabecera-listado";
import { Cargando } from "@/features/choferes/components/estados/cargando";
import { EstadoError } from "@/features/choferes/components/estados/error";
import { EstadoVacio } from "@/features/choferes/components/estados/vacio";
import { ListadoChoferes } from "@/features/choferes/components/listado-choferes";
import { Paginacion } from "@/features/choferes/components/paginacion";
import { listarChoferes, TAMANO_DE_PAGINA } from "@/lib/api/choferes";
import { ErrorApi } from "@/lib/api/http";
import {
  primeraFilaDeLaPagina,
  totalPaginas,
  ultimaFilaDeLaPagina,
} from "@/lib/utils/formato";

type SearchParams = PageProps<"/choferes">["searchParams"];

export const metadata = {
  title: "Choferes",
};

export default function PaginaChoferes({ searchParams }: PageProps<"/choferes">) {
  return (
    <div className="flex flex-col gap-7">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-sm font-medium text-orange-600">Personal operativo</p>
          <h2 className="text-2xl font-bold tracking-tight sm:text-3xl text-slate-950">
            Choferes
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Conductores registrados y asignación operativa de servicios.
          </p>
        </div>

        <div className="w-full sm:w-auto">
          <Suspense
            fallback={<div className="h-10 w-full sm:w-72 rounded-lg bg-slate-100" />}
          >
            <BuscadorConCriterio searchParams={searchParams} />
          </Suspense>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white shadow-none overflow-hidden p-6">
        <Suspense fallback={<Cargando />}>
          <Listado searchParams={searchParams} />
        </Suspense>
      </div>
    </div>
  );
}

async function BuscadorConCriterio({ searchParams }: { searchParams: SearchParams }) {
  const criterio = leerTexto(await searchParams, "q");
  return <BuscadorChoferes criterioInicial={criterio} />;
}

async function Listado({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const criterio = leerTexto(params, "q");
  const pagina = leerNumero(params, "page");

  let resultado;
  try {
    resultado = await listarChoferes({
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
      return <EstadoVacio criterio={criterio} rutaSinBusqueda="/choferes" />;
    }
    return <PaginaFueraDeRango pagina={pagina} />;
  }

  return (
    <div className="flex flex-col gap-6">
      <CabeceraListado titulo="Choferes" total={resultado.total} paginas={paginas} />

      <ListadoChoferes choferes={resultado.items} />

      <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-3 pt-2">
        <Paginacion paginaActual={resultado.page} paginas={paginas} criterio={criterio} />
        <p className="text-xs text-slate-500 tabular-nums">
          {`Mostrando ${primeraFilaDeLaPagina(
            resultado.page,
            TAMANO_DE_PAGINA,
          )}–${ultimaFilaDeLaPagina(
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
    <div role="status" className="border-t border-slate-200 py-10 text-center">
      <p className="text-base font-semibold text-slate-900">
        La página {pagina} no tiene choferes.
      </p>
      <p className="mt-2 text-sm text-slate-500">
        El listado no llega tan lejos. Volvé a empezar desde el principio.
      </p>
      <Link
        href="/choferes"
        className="mt-5 inline-flex min-h-10 items-center justify-center rounded-lg border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 shadow-xs hover:bg-slate-50"
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
) {
  const valor = leerTexto(params, clave);
  if (!/^\d+$/.test(valor)) {
    return 1;
  }
  return Math.max(1, Number.parseInt(valor, 10));
}
