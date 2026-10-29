import Link from "next/link";
import { Suspense } from "react";

import { listarChoferesActivos } from "@/lib/api/choferes";
import {
  listarTiposVehiculo,
  listarVehiculos,
  TAMANO_DE_PAGINA,
} from "@/lib/api/vehiculos";
import { ErrorApi } from "@/lib/api/http";
import { BuscadorVehiculos } from "@/features/vehiculos/components/buscador-vehiculos";
import { CabeceraListado } from "@/features/vehiculos/components/cabecera-listado";
import { NuevoVehiculo } from "@/features/vehiculos/components/nuevo-vehiculo";
import { Cargando } from "@/features/vehiculos/components/estados/cargando";
import { EstadoError } from "@/features/vehiculos/components/estados/error";
import { EstadoVacio } from "@/features/vehiculos/components/estados/vacio";
import { ListadoVehiculos } from "@/features/vehiculos/components/listado-vehiculos";
import { Paginacion } from "@/features/vehiculos/components/paginacion";
import { PanelTarifas } from "@/features/vehiculos/components/panel-tarifas";
import {
  primeraFilaDeLaPagina,
  totalPaginas,
  ultimaFilaDeLaPagina,
} from "@/lib/utils/formato";

type SearchParams = PageProps<"/vehiculos">["searchParams"];

export const metadata = {
  title: "Vehículos",
};

export default function PaginaVehiculos({ searchParams }: PageProps<"/vehiculos">) {
  return (
    <div className="flex flex-col gap-6">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
            Flota operativa
          </p>
          <h2 className="mt-1 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            Vehículos
          </h2>
          <p className="mt-1 text-xs text-[#7f8da1] dark:text-[#94a3b8]">
            Controlá la flota, las tarifas y los choferes habituales.
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
          {/* El diálogo se monta al abrirse y pide sus catálogos en ese momento. */}
          <NuevoVehiculo />
        </div>
      </div>

      {/* Tarifas reales por tipo de vehículo */}
      <Suspense
        fallback={
          <div className="h-56 rounded-2xl border border-[#e8edf4] bg-white p-6 dark:border-[#1e2c44] dark:bg-[#111c2e]" />
        }
      >
        <Tarifas />
      </Suspense>

      {/* Tabla completa de vehículos conectada a backend */}
      <div className="rounded-2xl border border-[#e8edf4] bg-white p-6 shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <Suspense fallback={<Cargando />}>
          <Listado searchParams={searchParams} />
        </Suspense>
      </div>
    </div>
  );
}

async function BuscadorConCriterio({ searchParams }: { searchParams: SearchParams }) {
  const criterio = leerTexto(await searchParams, "q");
  return <BuscadorVehiculos criterioInicial={criterio} />;
}

async function Tarifas() {
  let tipos;
  try {
    tipos = await listarTiposVehiculo();
  } catch (error) {
    if (error instanceof ErrorApi) {
      return <EstadoError clase={error.clase} />;
    }
    throw error;
  }
  return <PanelTarifas tipos={tipos} />;
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

  const [tiposVehiculo, choferes] = await Promise.all([
    listarTiposVehiculo().catch(() => []),
    listarChoferesActivos().catch(() => []),
  ]);

  return (
    <div className="flex flex-col gap-6">
      <CabeceraListado total={resultado.total} paginas={paginas} />

      <ListadoVehiculos
        vehiculos={resultado.items}
        tiposVehiculo={tiposVehiculo}
        choferes={choferes}
      />

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
        La página {pagina} no tiene vehículos.
      </p>
      <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
        El listado no llega tan lejos. Volvé a empezar desde el principio.
      </p>
      <Link
        href="/vehiculos"
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
