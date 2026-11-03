import { ArrowDownToLine } from "lucide-react";
import { connection } from "next/server";
import { Suspense } from "react";

import { BuscadorRendiciones } from "@/features/rendiciones/components/buscador-rendiciones";
import { EstadoError } from "@/features/rendiciones/components/estados/error";
import { EstadoVacioRendiciones } from "@/features/rendiciones/components/estados/vacio";
import { NuevaRendicion } from "@/features/rendiciones/components/nueva-rendicion";
import { PaginacionRendiciones } from "@/features/rendiciones/components/paginacion";
import { TablaRendiciones } from "@/features/rendiciones/components/tabla-rendiciones";
import type { ResumenRendiciones, ServicioElegible } from "@/features/rendiciones/types";
import { formatearMonto } from "@/features/rendiciones/utils";
import { ErrorApi } from "@/lib/api/http";
import {
  listarRendiciones,
  listarServiciosElegibles,
  TAMANO_DE_PAGINA,
} from "@/lib/api/rendiciones";
import {
  primeraFilaDeLaPagina,
  totalPaginas,
  ultimaFilaDeLaPagina,
} from "@/lib/utils/formato";

export const instant = false;

export const metadata = {
  title: "Rendiciones",
};

type Parametros = Record<string, string | string[] | undefined>;

export default function PaginaRendiciones({ searchParams }: PageProps<"/rendiciones">) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
            Control financiero
          </p>
          <h1 className="text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            Rendiciones
          </h1>
          <p className="mt-1 text-xs text-[#7f8da1] dark:text-[#94a3b8]">
            Revisá gastos, adelantos y cierres de cada servicio.
          </p>
        </div>

        <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row sm:items-center">
          <Suspense
            fallback={
              <div className="h-10 w-full rounded-xl bg-[#f1f3f6] sm:w-72 dark:bg-[#16253d]" />
            }
          >
            <BuscadorConCriterio searchParams={searchParams} />
          </Suspense>
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled
              title="Exportar CSV queda fuera de esta historia"
              className="flex items-center gap-1.5 rounded-xl border border-[#dfe6ef] bg-white px-3.5 py-2.5 text-xs font-semibold text-[#62738a] opacity-60 dark:border-[#1e2c44] dark:bg-[#111c2e] dark:text-[#cbd5e1]"
            >
              <ArrowDownToLine size={15} />
              <span>Exportar CSV</span>
            </button>
            <Suspense
              fallback={
                <div className="h-10 w-36 rounded-xl bg-[#f1f3f6] dark:bg-[#16253d]" />
              }
            >
              <NuevaRendicionConElegibles />
            </Suspense>
          </div>
        </div>
      </div>

      <Suspense fallback={<Cargando />}>
        <Contenido searchParams={searchParams} />
      </Suspense>
    </div>
  );
}

async function BuscadorConCriterio({
  searchParams,
}: {
  searchParams: PageProps<"/rendiciones">["searchParams"];
}) {
  await connection();
  const criterio = leerTexto(await searchParams, "q");
  return <BuscadorRendiciones criterioInicial={criterio} />;
}

async function NuevaRendicionConElegibles() {
  await connection();
  let servicios: ServicioElegible[] = [];
  try {
    servicios = await listarServiciosElegibles();
  } catch (error) {
    if (!(error instanceof ErrorApi)) {
      throw error;
    }
  }
  return <NuevaRendicion servicios={servicios} />;
}

async function Contenido({
  searchParams,
}: {
  searchParams: PageProps<"/rendiciones">["searchParams"];
}) {
  await connection();
  const parametros = await searchParams;
  const criterio = leerTexto(parametros, "q");
  const pagina = leerNumero(parametros, "page");

  let resultado;
  try {
    resultado = await listarRendiciones({
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

  return (
    <div className="flex flex-col gap-6">
      <Indicadores resumen={resultado.resumen} />

      <section className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm sm:p-6 dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-[#edf0f4] pb-4 dark:border-[#1e2c44]">
          <div>
            <h2 className="text-base font-bold text-[#172b4d] dark:text-white">
              Rendiciones de choferes
            </h2>
            <p className="mt-0.5 text-xs text-[#96a2b2] dark:text-[#94a3b8]">
              Controlá adelantos, gastos informados y saldos a pagar.
            </p>
          </div>
        </div>

        {resultado.items.length === 0 ? (
          <EstadoVacioRendiciones criterio={criterio} pagina={pagina} />
        ) : (
          <div className="flex flex-col gap-5">
            <TablaRendiciones rendiciones={resultado.items} />

            <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-3 pt-2">
              <PaginacionRendiciones
                paginaActual={resultado.page}
                paginas={paginas}
                criterio={criterio}
              />
              <p className="text-xs text-[#7f8da1] tabular-nums dark:text-[#94a3b8]">
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
        )}
      </section>
    </div>
  );
}

function Indicadores({ resumen }: { resumen: ResumenRendiciones }) {
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      <TarjetaIndicador
        titulo="Pendiente de rendición"
        valor={formatearMonto(resumen.pendiente_total)}
        detalle={`${resumen.pendiente_cantidad} rendiciones por cerrar`}
        claseDetalle="text-[#b86a16] dark:text-[#fbbf24]"
      />
      <TarjetaIndicador
        titulo="Aprobado este mes"
        valor={formatearMonto(resumen.aprobado_mes_total)}
        detalle="Rendiciones aprobadas en el mes corriente"
        claseDetalle="text-[#248952] dark:text-[#4ade80]"
      />
      <TarjetaIndicador
        titulo="Gastos informados"
        valor={formatearMonto(resumen.gastos_total)}
        detalle="Combustible, peajes y otros gastos"
        claseDetalle="text-[#2165d5] dark:text-[#60a5fa]"
      />
    </div>
  );
}

function TarjetaIndicador({
  titulo,
  valor,
  detalle,
  claseDetalle,
}: {
  titulo: string;
  valor: string;
  detalle: string;
  claseDetalle: string;
}) {
  return (
    <div className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
      <p className="text-xs font-medium text-[#8b99ab] dark:text-[#94a3b8]">{titulo}</p>
      <p className="mt-2 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
        {valor}
      </p>
      <p className={`mt-1 text-xs font-medium ${claseDetalle}`}>{detalle}</p>
    </div>
  );
}

function Cargando() {
  return (
    <div className="flex flex-col gap-4" aria-busy="true" aria-live="polite">
      <div className="h-28 animate-pulse rounded-2xl bg-[#f1f3f6] dark:bg-[#16253d]" />
      <div className="h-72 animate-pulse rounded-2xl bg-[#f1f3f6] dark:bg-[#16253d]" />
    </div>
  );
}

function leerTexto(params: Parametros, clave: string): string {
  const valor = params[clave];
  return typeof valor === "string" ? valor.trim() : "";
}

function leerNumero(params: Parametros, clave: string): number {
  const valor = leerTexto(params, clave);
  if (!/^\d+$/.test(valor)) {
    return 1;
  }
  return Math.max(1, Number.parseInt(valor, 10));
}
