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
import { cn } from "@/lib/utils/cn";
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

      <main className="mx-auto w-full max-w-5xl py-8 sm:px-6">
        <Suspense
          fallback={
            <p className="px-4 py-4 text-tinta-media sm:px-0">Cargando formulario…</p>
          }
        >
          <FormularioConCatalogos />
        </Suspense>
        <Suspense fallback={<Cargando />}>
          <ListadoConPagina searchParams={searchParams} />
        </Suspense>
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
        <>
          <CabeceraListado total={0} paginas={0} />
          <EstadoVacio />
        </>
      );
    }
    return <PaginaFueraDeRango pagina={pagina} />;
  }

  return (
    <div className="flex flex-col gap-6">
      <CabeceraListado total={resultado.total} paginas={paginas} />
      <ListadoServicios servicios={resultado.items} />
      <div className="flex flex-wrap items-center justify-between gap-x-8 gap-y-3 px-4 sm:px-0">
        <Paginacion paginaActual={resultado.page} paginas={paginas} />
        <p className="text-[0.8125rem] text-tinta-media tabular-nums">
          {`Mostrando ${primeraFilaDeLaPagina(resultado.page, resultado.size)}–${ultimaFilaDeLaPagina(
            resultado.page,
            resultado.size,
            resultado.total,
          )} de ${resultado.total}`}
        </p>
      </div>
    </div>
  );
}

function CabeceraListado({ total, paginas }: { total: number; paginas: number }) {
  return (
    <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 px-4 sm:px-0">
      <h1 className="text-[1.5rem] font-semibold leading-tight text-tinta">Servicios</h1>
      <p className="text-[0.875rem] text-tinta-media">
        {total === 1 ? "1 en total" : `${total} en total`}
        {paginas > 1 ? ` · ${paginas} páginas` : ""}
      </p>
    </div>
  );
}

function PaginaFueraDeRango({ pagina }: { pagina: number }) {
  return (
    <div role="status" className="border-t border-linea px-4 py-12 sm:px-0">
      <p className="text-[1rem] font-semibold text-tinta">
        La página {pagina} no tiene servicios.
      </p>
      <p className="mt-2 text-[0.875rem] text-tinta-media">
        El listado no llega tan lejos. Volvé a empezar desde el principio.
      </p>
      <Link
        href="/servicios"
        className="mt-5 inline-block rounded-[4px] border border-linea bg-white px-4 py-2 text-[0.875rem] font-medium text-senal hover:border-senal"
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
