import { Suspense } from "react";

import { Cotizador } from "@/features/cotizaciones/components/cotizador";
import { Cargando } from "@/features/servicios/components/estados/cargando";
import { EstadoError } from "@/features/servicios/components/estados/error";
import { listarTiposParaAlta } from "@/lib/api/servicios";
import { ErrorApi } from "@/lib/api/http";

export const metadata = {
  title: "Cotizaciones",
};

export default function PaginaCotizaciones() {
  return (
    <div className="flex flex-col gap-6">
      <Encabezado />
      <Suspense fallback={<Cargando />}>
        <Contenido />
      </Suspense>
    </div>
  );
}

async function Contenido() {
  let tiposVehiculo;
  try {
    tiposVehiculo = await listarTiposParaAlta();
  } catch (error) {
    if (error instanceof ErrorApi) {
      return <EstadoError clase={error.clase} />;
    }
    throw error;
  }
  return <Cotizador tiposVehiculo={tiposVehiculo} />;
}

function Encabezado() {
  return (
    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
      <div>
        <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
          Calculadora comercial
        </p>
        <h2 className="text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
          Cotizaciones
        </h2>
        <p className="mt-1 text-xs text-[#7f8da1] dark:text-[#94a3b8]">
          Armá presupuestos con las tarifas vigentes del sistema.
        </p>
      </div>
    </div>
  );
}
