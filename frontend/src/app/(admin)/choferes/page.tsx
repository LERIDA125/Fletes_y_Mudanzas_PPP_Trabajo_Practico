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
  const truckRates = [
    { type: "Camión chico", value: "$16.000", detail: "Hasta 12 m³ de capacidad" },
    { type: "Camión grande", value: "$24.000", detail: "Hasta 30 m³ de capacidad" },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5]">
            Personal operativo
          </p>
          <h2 className="text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl">
            Choferes
          </h2>
          <p className="mt-1 text-xs text-[#7f8da1]">
            Gestioná tu equipo, disponibilidad y tarifas operativas.
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

      {/* Tarjetas de Disponibilidad */}
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl border border-[#e8edf4] bg-white p-4 shadow-sm">
          <p className="text-xs font-medium text-[#8b99ab]">Libres hoy</p>
          <p className="mt-2 inline-flex rounded-lg bg-[#e9f8ef] px-2.5 py-1 text-xl font-bold text-[#248952]">
            3
          </p>
          <p className="mt-2 text-[10px] text-[#9aa7b7]">de 6 choferes registrados</p>
        </div>

        <div className="rounded-2xl border border-[#e8edf4] bg-white p-4 shadow-sm">
          <p className="text-xs font-medium text-[#8b99ab]">En viaje</p>
          <p className="mt-2 inline-flex rounded-lg bg-[#e9f4ff] px-2.5 py-1 text-xl font-bold text-[#2879bd]">
            2
          </p>
          <p className="mt-2 text-[10px] text-[#9aa7b7]">en servicios en curso</p>
        </div>

        <div className="rounded-2xl border border-[#e8edf4] bg-white p-4 shadow-sm">
          <p className="text-xs font-medium text-[#8b99ab]">Licencia</p>
          <p className="mt-2 inline-flex rounded-lg bg-[#f1edff] px-2.5 py-1 text-xl font-bold text-[#7951c9]">
            1
          </p>
          <p className="mt-2 text-[10px] text-[#9aa7b7]">franco programado</p>
        </div>
      </div>

      {/* Tarifario por vehículo */}
      <section className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h3 className="text-base font-bold text-[#172b4d]">Tarifario por vehículo</h3>
            <p className="mt-0.5 text-xs text-[#96a2b2]">
              Base sugerida para calcular cada servicio
            </p>
          </div>
          <span className="rounded-full bg-[#f4f8ff] px-3 py-1 text-xs font-semibold text-[#2165d5]">
            Vigente desde septiembre 2026
          </span>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {truckRates.map((rate) => (
            <div
              key={rate.type}
              className="flex items-center justify-between rounded-xl border border-[#edf0f4] bg-[#fbfcfd] p-4"
            >
              <div>
                <p className="text-xs font-bold text-[#172b4d]">{rate.type}</p>
                <p className="mt-0.5 text-[11px] text-[#96a2b2]">{rate.detail}</p>
              </div>
              <p className="text-base font-bold text-[#172b4d]">
                {rate.value}
                <span className="ml-1 text-[11px] font-normal text-[#96a2b2]">
                  / servicio
                </span>
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Tabla del equipo de choferes con datos reales */}
      <div className="rounded-2xl border border-[#e8edf4] bg-white p-6 shadow-sm">
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
