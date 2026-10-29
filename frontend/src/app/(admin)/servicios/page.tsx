import { Suspense } from "react";

import { FormularioServicio } from "@/features/servicios/components/formulario-servicio";
import { Cargando } from "@/features/servicios/components/estados/cargando";
import { EstadoError } from "@/features/servicios/components/estados/error";
import { EstadoVacio } from "@/features/servicios/components/estados/vacio";
import { ListadoServicios } from "@/features/servicios/components/listado-servicios";
import { Paginacion } from "@/features/servicios/components/paginacion";
import { listarServicios, TAMANO_DE_PAGINA } from "@/lib/api/servicios";
import { ErrorApi } from "@/lib/api/http";
import {
  primeraFilaDeLaPagina,
  totalPaginas,
  ultimaFilaDeLaPagina,
} from "@/lib/utils/formato";

type SearchParams = PageProps<"/servicios">["searchParams"];

export const metadata = {
  title: "Servicios",
};

export default function PaginaServicios({ searchParams }: PageProps<"/servicios">) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
            Resumen operativo
          </p>
          <h2 className="text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            Servicios
          </h2>
          <p className="mt-1 text-xs text-[#7f8da1] dark:text-[#94a3b8]">
            Gestioná la agenda, las asignaciones y el estado de cada servicio.
          </p>
        </div>

        {/* El fallback ya es el formulario real: el botón y el modal existen
            desde el primer render. El hijo solo espera `searchParams` para
            abrirlo cuando llega `?nuevo=1`; los catálogos se piden al abrir. */}
        <Suspense fallback={<FormularioServicio />}>
          <FormularioConParametro searchParams={searchParams} />
        </Suspense>
      </div>

      <Suspense fallback={<Cargando />}>
        <ListadoConPagina searchParams={searchParams} />
      </Suspense>
    </div>
  );
}

async function FormularioConParametro({ searchParams }: { searchParams: SearchParams }) {
  const parametros = await searchParams;
  return <FormularioServicio abrirInicial={parametros.nuevo === "1"} />;
}

async function ListadoConPagina({ searchParams }: { searchParams: SearchParams }) {
  const parametros = await searchParams;
  const pagina = leerNumero(parametros.page);

  let resultado;
  try {
    resultado = await listarServicios(pagina, TAMANO_DE_PAGINA);
  } catch (error) {
    if (error instanceof ErrorApi) {
      return <EstadoError clase={error.clase} />;
    }
    throw error;
  }

  const paginas = totalPaginas(resultado.total, resultado.size);

  return (
    <div className="flex flex-col gap-6">
      {/* Tarjeta contenedora de la tabla */}
      <div className="overflow-hidden rounded-2xl border border-[#e8edf4] bg-white shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <div className="flex flex-row items-center justify-between gap-4 border-b border-[#edf0f4] px-5 py-5 sm:px-6 dark:border-[#1e2c44]">
          <div>
            <h3 className="text-base font-bold text-[#172b4d] dark:text-white">
              Servicios registrados
            </h3>
            <p className="mt-0.5 text-xs text-[#96a2b2] dark:text-[#94a3b8]">
              Servicios programados y asignaciones operativas en curso.
            </p>
          </div>
          <p className="text-xs font-semibold text-[#5f7087] tabular-nums dark:text-[#cbd5e1]">
            {resultado.total === 1 ? "1 servicio" : `${resultado.total} servicios`}
          </p>
        </div>

        {resultado.items.length === 0 ? (
          <div className="p-6">
            <EstadoVacio />
          </div>
        ) : (
          <>
            <ListadoServicios servicios={resultado.items} />
            <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-3 border-t border-[#edf0f4] px-5 py-4 text-xs text-slate-500 sm:px-6 dark:border-[#1e2c44] dark:text-slate-400">
              <span>
                {`Mostrando ${primeraFilaDeLaPagina(
                  resultado.page,
                  resultado.size,
                )}–${ultimaFilaDeLaPagina(
                  resultado.page,
                  resultado.size,
                  resultado.total,
                )} de ${resultado.total} servicios`}
              </span>
              <Paginacion paginaActual={resultado.page} paginas={paginas} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function leerNumero(valor: string | string[] | undefined): number {
  if (typeof valor !== "string" || !/^\d+$/.test(valor)) {
    return 1;
  }
  return Math.max(1, Number.parseInt(valor, 10));
}
