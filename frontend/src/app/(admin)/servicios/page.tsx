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
import { cn } from "@/lib/utils/cn";
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

const RUTAS = [
  { href: "/", etiqueta: "Clientes" },
  { href: "/choferes", etiqueta: "Choferes" },
  { href: "/vehiculos", etiqueta: "Vehículos" },
  { href: "/servicios", etiqueta: "Servicios" },
];

export default function PaginaServicios({ searchParams }: PageProps<"/servicios">) {
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
                aria-current={ruta.href === "/servicios" ? "page" : undefined}
                className={cn(
                  "text-[0.9375rem] font-medium",
                  ruta.href === "/servicios"
                    ? "text-papel underline decoration-2 underline-offset-8"
                    : "text-papel/65 hover:text-papel",
                )}
              >
                {ruta.etiqueta}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6">
        <div className="flex flex-col gap-6">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-tinta sm:text-3xl">
                Servicios y Despacho
              </h1>
              <p className="mt-1 text-sm text-tinta-media">
                Control operativo de viajes, asignación de unidades y cotización oficial.
              </p>
            </div>
            <Suspense
              fallback={
                <span className="inline-flex min-h-10 items-center rounded-lg bg-panel-suave px-4 text-sm font-medium text-tinta-media">
                  Cargando formulario…
                </span>
              }
            >
              <FormularioConCatalogos />
            </Suspense>
          </div>

          {/* Tarjetas informativas de políticas operativas */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-linea bg-white p-4 shadow-xs">
              <span className="text-xs font-semibold uppercase tracking-wider text-tinta-media">
                Franquicia por viaje
              </span>
              <p className="mt-1 text-lg font-bold text-tinta">10 km bonificados</p>
              <p className="mt-0.5 text-xs text-tinta-media">
                Solo se tarifan los km de recorrido que superen la franquicia.
              </p>
            </div>

            <div className="rounded-xl border border-linea bg-white p-4 shadow-xs">
              <span className="text-xs font-semibold uppercase tracking-wider text-tinta-media">
                Distancia computable
              </span>
              <p className="mt-1 text-lg font-bold text-tinta">Ida y vuelta (2x)</p>
              <p className="mt-0.5 text-xs text-tinta-media">
                El kilometraje total se calcula automáticamente duplicando la ida.
              </p>
            </div>

            <div className="rounded-xl border border-linea bg-white p-4 shadow-xs">
              <span className="text-xs font-semibold uppercase tracking-wider text-tinta-media">
                Tarificación oficial
              </span>
              <p className="mt-1 text-lg font-bold text-tinta">Calculada en servidor</p>
              <p className="mt-0.5 text-xs text-tinta-media">
                Aplica la tarifa horaria y de km vigente del tipo de vehículo
                seleccionado.
              </p>
            </div>
          </div>

          <Suspense fallback={<Cargando />}>
            <ListadoConPagina searchParams={searchParams} />
          </Suspense>
        </div>
      </main>
    </>
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
        <div className="overflow-hidden rounded-xl border border-linea bg-white shadow-xs">
          <CabeceraListado total={0} paginas={0} />
          <EstadoVacio />
        </div>
      );
    }
    return <PaginaFueraDeRango pagina={pagina} />;
  }

  return (
    <div className="overflow-hidden rounded-xl border border-linea bg-white shadow-xs">
      <CabeceraListado total={resultado.total} paginas={paginas} />
      <ListadoServicios servicios={resultado.items} />
      <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-3 border-t border-linea bg-white px-4 py-3 sm:px-6">
        <p className="order-2 text-xs tabular-nums text-tinta-media sm:order-1">
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
    <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-2 border-b border-linea bg-papel px-4 py-3 sm:px-6">
      <h2 className="text-sm font-semibold tracking-wide text-tinta">
        Registro de servicios
      </h2>
      <p className="text-xs text-tinta-media">
        {total === 1 ? "1 servicio registrado" : `${total} servicios registrados`}
        {paginas > 1 ? ` · ${paginas} páginas` : ""}
      </p>
    </div>
  );
}

function PaginaFueraDeRango({ pagina }: { pagina: number }) {
  return (
    <div
      role="status"
      className="rounded-xl border border-linea bg-white p-8 text-center shadow-xs"
    >
      <p className="text-base font-semibold text-tinta">
        La página {pagina} no tiene servicios.
      </p>
      <p className="mt-2 text-sm text-tinta-media">
        El listado no llega tan lejos. Volvé a empezar desde el principio.
      </p>
      <Link
        href="/servicios"
        className="mt-5 inline-flex min-h-10 items-center justify-center rounded-lg border border-linea bg-white px-4 text-sm font-medium text-tinta shadow-xs transition-colors hover:bg-papel"
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
