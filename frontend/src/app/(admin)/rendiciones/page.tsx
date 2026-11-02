import { ArrowDownToLine, ReceiptText } from "lucide-react";

import { PanelCajaRendiciones } from "@/features/servicios/components/panel-caja-rendiciones";
import type { Servicio } from "@/features/servicios/types";
import { listarServicios } from "@/lib/api/servicios";

export default async function PaginaRendiciones() {
  let servicios: Servicio[] = [];

  try {
    const respuesta = await listarServicios(1, 100);
    servicios = respuesta.items;
  } catch {
    servicios = [];
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa] flex items-center gap-1.5">
            <ReceiptText size={14} />
            Control Financiero y Caja
          </p>
          <h1 className="text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            Caja y Rendiciones de Choferes
          </h1>
          <p className="mt-1 text-xs text-[#7f8da1] dark:text-[#94a3b8]">
            Validación de comprobantes de remito firmado (POD), dinero en efectivo cobrado
            y conciliación de saldos de caja.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className="flex items-center gap-1.5 rounded-xl border border-[#dfe6ef] bg-white px-3.5 py-2.5 text-xs font-semibold text-[#62738a] shadow-xs hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:bg-[#111c2e] dark:text-[#cbd5e1] dark:hover:bg-[#16253d]"
          >
            <ArrowDownToLine size={15} />
            <span>Exportar Rendiciones</span>
          </button>
        </div>
      </div>

      {/* Panel interactivo de rendiciones */}
      <PanelCajaRendiciones serviciosIniciales={servicios} />
    </div>
  );
}
