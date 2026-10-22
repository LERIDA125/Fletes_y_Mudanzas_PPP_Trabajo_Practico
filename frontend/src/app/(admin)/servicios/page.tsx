import Link from "next/link";
import { Suspense } from "react";

import { FormularioServicio } from "@/features/servicios/components/formulario-servicio";
import { Cargando } from "@/features/servicios/components/estados/cargando";
import { EstadoError } from "@/features/servicios/components/estados/error";
import { EstadoVacio } from "@/features/servicios/components/estados/vacio";
import { ListadoServicios } from "@/features/servicios/components/listado-servicios";
import { Paginacion } from "@/features/servicios/components/paginacion";
import {
  listarClientesParaAlta,
  listarServicios,
  listarTiposParaAlta,
  TAMANO_DE_PAGINA,
} from "@/lib/api/servicios";
import { ErrorApi } from "@/lib/api/http";
import type { ClienteOpcion, TipoVehiculoOpcion } from "@/features/servicios/types";
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
    <section className="flex flex-col gap-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[#0b1c30] sm:text-3xl">
            Servicios
          </h1>
          <p className="mt-1 text-sm text-[#545f73]">
            Consultá los viajes registrados y solicitá una cotización oficial.
          </p>
        </div>

        <Suspense
          fallback={
            <span className="inline-flex min-h-10 items-center rounded-lg bg-white px-4 text-sm font-medium text-[#545f73]">
              Cargando formulario…
            </span>
          }
        >
          <FormularioConCatalogos />
        </Suspense>
      </div>

      <Suspense fallback={<Cargando />}>
        <ListadoConPagina searchParams={searchParams} />
      </Suspense>
    </section>
  );
}

async function FormularioConCatalogos() {
  let clientes: ClienteOpcion[] = [];
  let tiposVehiculo: TipoVehiculoOpcion[] = [];
  let errorApi: ErrorApi | null = null;
  try {
    [clientes, tiposVehiculo] = await Promise.all([
      listarClientesParaAlta(),
      listarTiposParaAlta(),
    ]);
  } catch (error) {
    if (error instanceof ErrorApi) {
      errorApi = error;
    } else {
      throw error;
    }
  }
  if (errorApi) {
    return <EstadoError clase={errorApi.clase} />;
  }
  return <FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />;
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
  if (resultado.items.length === 0) {
    if (resultado.total === 0) {
      return (
        <div className="overflow-hidden rounded-xl border border-[#c6c6cd]/60 bg-white shadow-xs">
          <CabeceraListado total={0} paginas={0} />
          <EstadoVacio />
        </div>
      );
    }
    return <PaginaFueraDeRango pagina={pagina} />;
  }

  return (
    <div className="overflow-hidden rounded-xl border border-[#c6c6cd]/60 bg-white shadow-xs">
      <CabeceraListado total={resultado.total} paginas={paginas} />
      <ListadoServicios servicios={resultado.items} />
      <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-3 border-t border-[#c6c6cd]/50 bg-white px-5 py-3.5">
        <p className="order-2 text-xs tabular-nums text-[#545f73] sm:order-1">
          {`Mostrando ${primeraFilaDeLaPagina(resultado.page, resultado.size)}–${ultimaFilaDeLaPagina(
            resultado.page,
            resultado.size,
            resultado.total,
          )} de ${resultado.total}`}
        </p>
        <div className="order-1 sm:order-2">
          <Paginacion paginaActual={resultado.page} paginas={paginas} />
        </div>
      </div>
    </div>
  );
}

function CabeceraListado({ total, paginas }: { total: number; paginas: number }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-1 border-b border-[#c6c6cd]/40 bg-white px-5 py-4">
      <h2 className="text-sm font-semibold tracking-wide text-[#0b1c30]">
        Registro de servicios
      </h2>
      <p className="text-xs text-[#545f73]">
        {total === 1 ? "1 en total" : `${total} en total`}
        {paginas > 1 ? ` · ${paginas} páginas` : ""}
      </p>
    </div>
  );
}

function PaginaFueraDeRango({ pagina }: { pagina: number }) {
  return (
    <div
      role="status"
      className="rounded-xl border border-[#c6c6cd]/60 bg-white p-10 text-center shadow-xs"
    >
      <p className="text-base font-semibold text-[#0b1c30]">
        La página {pagina} no tiene servicios.
      </p>
      <p className="mt-2 text-sm text-[#545f73]">
        El listado no llega tan lejos. Volvé a empezar desde el principio.
      </p>
      <Link
        href="/servicios"
        className="mt-5 inline-flex min-h-10 items-center justify-center rounded-lg border border-[#c6c6cd] bg-white px-4 text-sm font-medium text-[#0b1c30] shadow-xs transition-colors hover:bg-[#eff4ff]"
      >
        Ir a la primera página
      </Link>
    </div>
  );
}

function leerNumero(valor: string | string[] | undefined): number {
  if (typeof valor !== "string" || !/^\d+$/.test(valor)) {
    return 1;
  }
  return Math.max(1, Number.parseInt(valor, 10));
}
