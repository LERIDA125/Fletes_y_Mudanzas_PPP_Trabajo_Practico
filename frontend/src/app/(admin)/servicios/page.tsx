import {
  CircleDollarSign,
  ClipboardList,
  MoreHorizontal,
  Search,
  UserRound,
  WalletCards,
} from "lucide-react";
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
    <div className="flex flex-col gap-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5]">
            Resumen operativo
          </p>
          <h2 className="text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl">
            Servicios
          </h2>
          <p className="mt-1 text-xs text-[#7f8da1]">
            Este es el estado de tu operación para hoy.
          </p>
        </div>

        <Suspense
          fallback={
            <span className="inline-flex min-h-10 items-center rounded-lg bg-white px-4 text-xs font-medium text-slate-500">
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
    </div>
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

  return (
    <div className="flex flex-col gap-6">
      {/* Indicadores clave */}
      <section
        className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
        aria-label="Indicadores clave"
      >
        <div className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-medium text-[#8492a6]">Servicios registrados</p>
              <p className="mt-2 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl">
                {resultado.total}
              </p>
            </div>
            <div className="flex size-9 items-center justify-center rounded-xl bg-[#edf4ff] text-[#2165d5]">
              <ClipboardList className="size-4" />
            </div>
          </div>
          <p className="mt-3 flex items-center gap-1 text-[11px] text-[#8b99ab]">
            <span className="font-semibold text-[#248952]">+12,5%</span> vs. semana pasada
          </p>
        </div>

        <div className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-medium text-[#8492a6]">Choferes disponibles</p>
              <p className="mt-2 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl">
                3
              </p>
            </div>
            <div className="flex size-9 items-center justify-center rounded-xl bg-[#e9f8ef] text-[#248952]">
              <UserRound className="size-4" />
            </div>
          </div>
          <p className="mt-3 flex items-center gap-1 text-[11px] text-[#8b99ab]">
            <span className="font-semibold text-[#172b4d]">de 6</span> en la flota activa
          </p>
        </div>

        <div className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-medium text-[#8492a6]">Dinero por cobrar hoy</p>
              <p className="mt-2 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl">
                $150.000
              </p>
            </div>
            <div className="flex size-9 items-center justify-center rounded-xl bg-[#fff4e5] text-[#b86a16]">
              <CircleDollarSign className="size-4" />
            </div>
          </div>
          <p className="mt-3 flex items-center gap-1 text-[11px] text-[#8b99ab]">
            <span className="font-semibold text-[#b86a16]">4 servicios</span> pendientes
          </p>
        </div>

        <div className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-medium text-[#8492a6]">Pendiente de rendición</p>
              <p className="mt-2 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl">
                $50.000
              </p>
            </div>
            <div className="flex size-9 items-center justify-center rounded-xl bg-[#f1edff] text-[#7951c9]">
              <WalletCards className="size-4" />
            </div>
          </div>
          <p className="mt-3 flex items-center gap-1 text-[11px] text-[#8b99ab]">
            <span className="font-semibold text-[#7951c9]">2 rendiciones</span> abiertas
          </p>
        </div>
      </section>

      {/* Tarjeta contenedora de la tabla */}
      <div className="rounded-2xl border border-[#e8edf4] bg-white shadow-sm overflow-hidden">
        <div className="flex flex-row items-center justify-between gap-4 border-b border-[#edf0f4] px-5 py-5 sm:px-6">
          <div>
            <h3 className="text-base font-bold text-[#172b4d]">Próximos Servicios</h3>
            <p className="mt-0.5 text-xs text-[#96a2b2]">
              Servicios programados y asignaciones operativas en curso.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-[#e5eaf1] bg-white px-3 py-1.5 text-xs font-semibold text-[#5f7087] shadow-xs hover:bg-[#f6f8fb]"
            >
              <Search className="size-3.5 text-[#99a7b8]" />
              <span>Buscar</span>
            </button>
            <button
              type="button"
              className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
              aria-label="Más opciones"
            >
              <MoreHorizontal className="size-4" />
            </button>
          </div>
        </div>

        {resultado.items.length === 0 ? (
          <div className="p-6">
            <EstadoVacio />
          </div>
        ) : (
          <>
            <ListadoServicios servicios={resultado.items} />
            <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-3 border-t border-[#edf0f4] px-5 py-4 text-xs text-slate-500 sm:px-6">
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
