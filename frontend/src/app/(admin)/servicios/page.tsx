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

const NAVEGACION = [
  { href: "/", etiqueta: "Clientes", icono: "groups" },
  { href: "/choferes", etiqueta: "Choferes", icono: "driver" },
  { href: "/vehiculos", etiqueta: "Vehículos", icono: "vehicle" },
  { href: "/servicios", etiqueta: "Servicios", icono: "truck" },
] as const;

export default function PaginaServicios({ searchParams }: PageProps<"/servicios">) {
  return (
    <div className="flex min-h-screen bg-panel-fondo text-panel-texto">
      <aside className="hidden w-60 shrink-0 flex-col border-r border-panel-borde bg-panel-superficie px-3 py-4 md:flex">
        <Link
          href="/servicios"
          className="flex items-center gap-3 border-b border-panel-borde px-2 pb-4"
        >
          <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-panel-primario text-white">
            <Icono nombre="truck" className="size-5" />
          </span>
          <span className="min-w-0">
            <span className="block truncate text-sm font-semibold">Fletes y Mudanzas</span>
            <span className="block truncate text-xs text-panel-secundario">
              Operaciones Express
            </span>
          </span>
        </Link>
        <nav aria-label="Secciones" className="mt-5 flex flex-col gap-1">
          {NAVEGACION.map((item) => {
            const activo = item.href === "/servicios";
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={activo ? "page" : undefined}
                className={`flex items-center gap-3 rounded-md border-l-2 px-3 py-2.5 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul ${
                  activo
                    ? "border-panel-primario bg-panel-suave text-panel-primario"
                    : "border-transparent text-panel-secundario hover:bg-panel-suave hover:text-panel-texto"
                }`}
              >
                <Icono nombre={item.icono} className="size-5" />
                {item.etiqueta}
              </Link>
            );
          })}
        </nav>
        <div className="mt-auto border-t border-panel-borde px-2 pt-4 text-xs leading-5 text-panel-secundario">
          Panel de administración
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex min-h-14 items-center justify-between gap-4 border-b border-panel-borde bg-panel-superficie px-4 sm:px-6">
          <div className="flex min-w-0 items-center gap-2 text-sm">
            <span className="hidden text-panel-secundario sm:inline">Operaciones</span>
            <span aria-hidden="true" className="hidden text-panel-borde sm:inline">
              /
            </span>
            <span className="font-semibold">Servicios</span>
          </div>
          <span className="hidden text-sm text-panel-secundario sm:inline">
            Fletes y Mudanzas Express
          </span>
        </header>
        <nav
          aria-label="Secciones"
          className="flex gap-1 overflow-x-auto border-b border-panel-borde bg-panel-superficie px-3 py-2 md:hidden"
        >
          {NAVEGACION.map((item) => {
            const activo = item.href === "/servicios";
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={activo ? "page" : undefined}
                className={`inline-flex min-h-10 shrink-0 items-center gap-2 rounded-md px-3 text-sm font-medium ${
                  activo
                    ? "bg-panel-suave text-panel-primario"
                    : "text-panel-secundario hover:bg-panel-suave"
                }`}
              >
                <Icono nombre={item.icono} className="size-4" />
                {item.etiqueta}
              </Link>
            );
          })}
        </nav>

        <main className="mx-auto flex w-full max-w-[1600px] flex-1 flex-col gap-5 p-4 sm:p-6">
          <section className="flex flex-col gap-5">
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div>
                <h1 className="text-2xl font-semibold tracking-tight text-panel-texto">
                  Servicios
                </h1>
                <p className="mt-1 max-w-2xl text-sm leading-5 text-panel-secundario">
                  Consultá los viajes registrados y solicitá una cotización oficial.
                </p>
              </div>
              <Suspense
                fallback={
                  <span className="inline-flex min-h-10 items-center rounded-md bg-panel-suave px-4 text-sm text-panel-secundario">
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
        </main>
      </div>
    </div>
  );
}

function Icono({
  nombre,
  className,
}: {
  nombre: "groups" | "driver" | "vehicle" | "truck";
  className?: string;
}) {
  const paths = {
    groups: (
      <>
        <path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="10" cy="7" r="4" />
        <path d="M20 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
      </>
    ),
    driver: (
      <>
        <circle cx="12" cy="8" r="4" />
        <path d="M5 21a7 7 0 0 1 14 0M19 8h3m-1.5-1.5v3" />
      </>
    ),
    vehicle: (
      <>
        <path d="M3 7h11v11H3zM14 11h4l3 3v4h-7z" />
        <circle cx="7.5" cy="18.5" r="1.5" />
        <circle cx="17.5" cy="18.5" r="1.5" />
      </>
    ),
    truck: (
      <>
        <path d="M3 6h12v12H3zM15 10h4l3 4v4h-7z" />
        <circle cx="7.5" cy="18.5" r="1.5" />
        <circle cx="18.5" cy="18.5" r="1.5" />
      </>
    ),
  };
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.7"
      viewBox="0 0 24 24"
    >
      {paths[nombre]}
    </svg>
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
        <div className="overflow-hidden rounded-lg border border-panel-borde bg-panel-superficie">
          <CabeceraListado total={0} paginas={0} />
          <EstadoVacio />
        </div>
      );
    }
    return <PaginaFueraDeRango pagina={pagina} />;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-panel-borde bg-panel-superficie">
      <CabeceraListado total={resultado.total} paginas={paginas} />
      <ListadoServicios servicios={resultado.items} />
      <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-3 border-t border-panel-borde bg-panel-superficie px-4 py-3">
        <p className="order-2 text-xs tabular-nums text-panel-secundario sm:order-1">
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
    <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-1 border-b border-panel-borde px-4 py-3">
      <h2 className="text-base font-semibold text-panel-texto">Registro de servicios</h2>
      <p className="text-xs text-panel-secundario">
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
      className="rounded-lg border border-panel-borde bg-panel-superficie px-5 py-10"
    >
      <p className="text-base font-semibold text-panel-texto">
        La página {pagina} no tiene servicios.
      </p>
      <p className="mt-2 text-sm text-panel-secundario">
        El listado no llega tan lejos. Volvé a empezar desde el principio.
      </p>
      <Link
        href="/servicios"
        className="mt-5 inline-flex min-h-10 items-center rounded-md border border-panel-borde bg-panel-superficie px-4 text-sm font-medium text-panel-texto hover:bg-panel-suave"
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
