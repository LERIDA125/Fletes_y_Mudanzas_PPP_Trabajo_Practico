"use client";

import { useState } from "react";

import { DialogoDetalleRendicion } from "@/features/rendiciones/components/dialogo-detalle-rendicion";
import { EtiquetaEstadoRendicion } from "@/features/rendiciones/components/estado-rendicion";
import type { Rendicion } from "@/features/rendiciones/types";
import { formatearFecha, formatearMonto } from "@/features/rendiciones/utils";

export function TablaRendiciones({ rendiciones }: { rendiciones: Rendicion[] }) {
  const [seleccionada, setSeleccionada] = useState<Rendicion | null>(null);

  return (
    <>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] text-left text-xs">
          <thead>
            <tr className="border-b border-[#f0f2f5] text-[10px] font-bold uppercase tracking-wider text-[#a0adbd] dark:border-[#1e2c44] dark:text-[#64748b]">
              <th className="px-3.5 py-3">Rendición</th>
              <th className="px-3.5 py-3">Chofer</th>
              <th className="px-3.5 py-3">Cliente</th>
              <th className="px-3.5 py-3">Fecha</th>
              <th className="px-3.5 py-3">Tarifa</th>
              <th className="px-3.5 py-3">Adelanto</th>
              <th className="px-3.5 py-3">Saldo</th>
              <th className="px-3.5 py-3">Estado</th>
              <th className="px-3.5 py-3 text-right">Acción</th>
            </tr>
          </thead>
          <tbody>
            {rendiciones.map((rendicion) => (
              <tr
                key={rendicion.id}
                className="border-b border-[#f1f3f6] text-xs transition hover:bg-[#fafcff] last:border-0 dark:border-[#1e2c44] dark:hover:bg-[#16253d]"
              >
                <td className="px-3.5 py-4 font-bold text-[#2165d5] dark:text-[#60a5fa]">
                  {rendicion.codigo}
                </td>
                <td className="px-3.5 py-4 font-semibold text-[#172b4d] dark:text-white">
                  {rendicion.nombre_chofer}
                </td>
                <td className="max-w-[220px] truncate px-3.5 py-4 text-[#718096] dark:text-[#94a3b8]">
                  {rendicion.razon_social_cliente}
                </td>
                <td className="px-3.5 py-4 text-[#718096] dark:text-[#94a3b8]">
                  {formatearFecha(rendicion.fecha)}
                </td>
                <td className="px-3.5 py-4 font-semibold text-[#172b4d] dark:text-white">
                  {formatearMonto(rendicion.tarifa)}
                </td>
                <td className="px-3.5 py-4 text-[#718096] dark:text-[#94a3b8]">
                  {formatearMonto(rendicion.adelanto)}
                </td>
                <td className="px-3.5 py-4 font-semibold text-[#172b4d] dark:text-white">
                  {formatearMonto(rendicion.saldo)}
                </td>
                <td className="px-3.5 py-4">
                  <EtiquetaEstadoRendicion estado={rendicion.estado} />
                </td>
                <td className="px-3.5 py-4 text-right">
                  <button
                    type="button"
                    onClick={() => setSeleccionada(rendicion)}
                    className="font-bold text-[#2165d5] hover:underline dark:text-[#60a5fa]"
                  >
                    Ver detalle
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {seleccionada ? (
        <DialogoDetalleRendicion
          rendicion={seleccionada}
          onCerrar={() => setSeleccionada(null)}
        />
      ) : null}
    </>
  );
}
