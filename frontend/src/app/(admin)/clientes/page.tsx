import Link from "next/link";
import { Suspense } from "react";
import { connection } from "next/server";

import { BuscadorClientes } from "@/features/clientes/components/buscador-clientes";
import { CabeceraListado } from "@/features/clientes/components/cabecera-listado";
import { Cargando } from "@/features/clientes/components/estados/cargando";
import { EstadoError } from "@/features/clientes/components/estados/error";
import { EstadoVacio } from "@/features/clientes/components/estados/vacio";
import { ListadoClientes } from "@/features/clientes/components/listado-clientes";
import { NuevoCliente } from "@/features/clientes/components/nuevo-cliente";
import { Paginacion } from "@/features/clientes/components/paginacion";
import { listarClientes, TAMANO_DE_PAGINA } from "@/lib/api/clientes";
import { ErrorApi } from "@/lib/api/http";
import {
  primeraFilaDeLaPagina,
  totalPaginas,
  ultimaFilaDeLaPagina,
} from "@/lib/utils/formato";
export const instant = false;

type SearchParams = PageProps<"/clientes">["searchParams"];

export const metadata = {
  title: "Clientes",
};

export default function PaginaClientes({ searchParams }: PageProps<"/clientes">) {
  return (
    <div className="flex flex-col gap-6">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div className="flex items-center gap-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
              Padrón operativo
            </p>
            <span className="rounded-full bg-[#edf4ff] px-2.5 py-0.5 text-[11px] font-bold text-[#2165d5] dark:bg-[#1a3356] dark:text-[#93c5fd]">
              Clientes activos
            </span>
          </div>
          <h2 className="mt-1 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            Clientes
          </h2>
          <p className="mt-1 text-xs text-[#7f8da1] dark:text-[#94a3b8]">
            Administrá contactos, historial y datos para cotizar más rápido.
          </p>
        </div>

        <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row sm:items-center">
          <Suspense
            fallback={
              <div className="h-10 w-full rounded-lg bg-slate-100 sm:w-72 dark:bg-slate-800" />
            }
          >
            <BuscadorConCriterio searchParams={searchParams} />
          </Suspense>
          <NuevoCliente />
        </div>
      </div>

      <div className="rounded-2xl border border-[#e8edf4] bg-white p-6 shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <Suspense fallback={<Cargando />}>
          <Listado searchParams={searchParams} />
        </Suspense>
      </div>
    </div>
  );
}

async function BuscadorConCriterio({ searchParams }: { searchParams: SearchParams }) {
  await connection();
  const criterio = leerTexto(await searchParams, "q");
  return <BuscadorClientes criterioInicial={criterio} />;
}

async function Listado({ searchParams }: { searchParams: SearchParams }) {
  await connection();
  const params = await searchParams;
  const criterio = leerTexto(params, "q");
  const pagina = leerNumero(params, "page");

  let resultado;
  try {
    resultado = await listarClientes({
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
      return <EstadoVacio criterio={criterio} rutaSinBusqueda="/clientes" />;
    }
    return <PaginaFueraDeRango pagina={pagina} />;
  }

  return (
    <div className="flex flex-col gap-6">
      <CabeceraListado total={resultado.total} paginas={paginas} />

      <ListadoClientes clientes={resultado.items} />

      <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-3 pt-2">
        <Paginacion paginaActual={resultado.page} paginas={paginas} criterio={criterio} />
        <p className="text-xs text-slate-500 tabular-nums dark:text-slate-400">
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
    <div
      role="status"
      className="border-t border-slate-200 py-10 text-center dark:border-slate-800"
    >
      <p className="text-base font-semibold text-slate-900 dark:text-white">
        La página {pagina} no tiene clientes.
      </p>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
        El listado no llega tan lejos. Volvé a empezar desde el principio.
      </p>
      <Link
        href="/clientes"
        className="mt-5 inline-flex min-h-10 items-center justify-center rounded-lg border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 shadow-xs hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
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
