import Link from "next/link";
import { Suspense } from "react";
import { Truck } from "lucide-react";

import { BuscadorVehiculos } from "@/features/vehiculos/components/buscador-vehiculos";
import { CabeceraListado } from "@/features/vehiculos/components/cabecera-listado";
import { Cargando } from "@/features/vehiculos/components/estados/cargando";
import { EstadoError } from "@/features/vehiculos/components/estados/error";
import { EstadoVacio } from "@/features/vehiculos/components/estados/vacio";
import { ListadoVehiculos } from "@/features/vehiculos/components/listado-vehiculos";
import { Paginacion } from "@/features/vehiculos/components/paginacion";
import { listarVehiculos, TAMANO_DE_PAGINA } from "@/lib/api/vehiculos";
import { ErrorApi } from "@/lib/api/http";
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
  const fleetSample = [
    {
      name: "Móvil 01",
      model: "Mercedes Benz Sprinter",
      size: "Grande",
      status: "Disponible",
      statusColor: "bg-[#e9f8ef] text-[#248952] dark:bg-[#163827] dark:text-[#4ade80]",
      km: "156.240 km",
    },
    {
      name: "Móvil 02",
      model: "Iveco Daily",
      size: "Grande",
      status: "En viaje",
      statusColor: "bg-[#e9f4ff] text-[#2879bd] dark:bg-[#1a3356] dark:text-[#60a5fa]",
      km: "204.820 km",
    },
    {
      name: "Móvil 03",
      model: "Renault Master",
      size: "Grande",
      status: "Disponible",
      statusColor: "bg-[#e9f8ef] text-[#248952] dark:bg-[#163827] dark:text-[#4ade80]",
      km: "98.430 km",
    },
    {
      name: "Móvil 04",
      model: "Fiat Ducato",
      size: "Chico",
      status: "Mantenimiento",
      statusColor: "bg-[#f1edff] text-[#7951c9] dark:bg-[#2b1f48] dark:text-[#c084fc]",
      km: "121.090 km",
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div className="flex items-center gap-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
              Flota operativa
            </p>
            <span className="rounded-full bg-[#e9f8ef] px-2.5 py-0.5 text-[11px] font-bold text-[#248952] dark:bg-[#163827] dark:text-[#4ade80]">
              3 disponibles
            </span>
          </div>
          <h2 className="mt-1 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            Vehículos
          </h2>
          <p className="mt-1 text-xs text-[#7f8da1] dark:text-[#94a3b8]">
            Controlá tu flota, capacidad, estado y mantenimiento.
          </p>
        </div>

        <div className="w-full sm:w-auto">
          <Suspense
            fallback={
              <div className="h-10 w-full sm:w-72 rounded-lg bg-slate-100 dark:bg-slate-800" />
            }
          >
            <BuscadorConCriterio searchParams={searchParams} />
          </Suspense>
        </div>
      </div>

      {/* Tarjetas resumen de unidades */}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {fleetSample.map((v) => (
          <article
            key={v.name}
            className="rounded-2xl border border-[#e8edf4] bg-white p-4 shadow-sm transition hover:shadow-md dark:border-[#1e2c44] dark:bg-[#111c2e]"
          >
            <div className="flex items-start justify-between">
              <div className="grid size-10 place-items-center rounded-xl bg-[#edf4ff] text-[#2165d5] dark:bg-[#1a3356] dark:text-[#60a5fa]">
                <Truck size={18} />
              </div>
              <span
                className={`inline-flex rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${v.statusColor}`}
              >
                {v.status}
              </span>
            </div>
            <h3 className="mt-3 text-sm font-bold text-[#172b4d] dark:text-white">
              {v.name}
            </h3>
            <p className="mt-0.5 text-xs text-[#718096] dark:text-[#94a3b8]">{v.model}</p>
            <div className="mt-3 flex justify-between border-t border-[#f0f2f5] pt-2.5 text-xs dark:border-[#1e2c44]">
              <span className="text-[#96a2b2] dark:text-[#64748b]">Tipo</span>
              <span className="font-bold text-[#172b4d] dark:text-white">
                Camión {v.size.toLowerCase()}
              </span>
            </div>
            <div className="mt-1.5 flex justify-between text-xs">
              <span className="text-[#96a2b2] dark:text-[#64748b]">Kilometraje</span>
              <span className="font-semibold text-[#5c6d83] dark:text-[#cbd5e1]">
                {v.km}
              </span>
            </div>
          </article>
        ))}
      </div>

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
