"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { MoreHorizontal, Trash2 } from "lucide-react";

import type { Chofer } from "@/features/choferes/types";
import { eliminarVehiculo } from "@/features/vehiculos/actions";
import { fechaCorta } from "@/lib/utils/formato";

import type { TipoVehiculo, Vehiculo } from "../types";
import { DialogoVehiculo } from "./dialogo-vehiculo";

const formatoCapacidad = new Intl.NumberFormat("es-AR", {
  maximumFractionDigits: 2,
});

type Propiedades = {
  vehiculo: Vehiculo;
  tiposVehiculo?: TipoVehiculo[];
  choferes?: Chofer[];
};

export function FilaVehiculo({
  vehiculo,
  tiposVehiculo = [],
  choferes = [],
}: Propiedades) {
  const router = useRouter();
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [dialogoAbierto, setDialogoAbierto] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");

  async function confirmarBaja() {
    const confirmado = window.confirm(
      `¿Dar de baja el vehículo ${vehiculo.patente}? Esta acción no se puede deshacer.`,
    );
    if (!confirmado) {
      return;
    }

    setMensajeError("");
    setEnviando(true);
    try {
      const resultado = await eliminarVehiculo(vehiculo.id);
      if (!resultado.ok) {
        setMensajeError(resultado.mensaje);
        return;
      }
      setMenuAbierto(false);
      router.refresh();
    } finally {
      setEnviando(false);
    }
  }

  return (
    <tr className="border-t border-linea align-top max-sm:block">
      <th
        scope="row"
        className="break-words px-4 py-4 text-left text-[1rem] font-semibold text-tinta max-sm:block sm:px-0 sm:pr-4"
      >
        {vehiculo.patente}
      </th>
      <td className="break-words px-4 py-1 text-[0.875rem] text-tinta max-sm:block sm:px-0 sm:py-4 sm:pr-4">
        <span className="text-tinta-media sm:hidden">Tipo y capacidad: </span>
        <span>{vehiculo.descripcion_tipo_vehiculo}</span>
        <span className="block text-tinta-media">
          {formatoCapacidad.format(vehiculo.capacidad_carga_kg)} kg
        </span>
      </td>
      <td className="break-words px-4 py-1 text-[0.875rem] text-tinta max-sm:block sm:px-0 sm:py-4 sm:pr-4">
        <span className="text-tinta-media sm:hidden">Chofer habitual: </span>
        {vehiculo.nombre_chofer_habitual ?? "Sin chofer habitual"}
      </td>
      <td className="px-4 py-1 text-right text-[0.875rem] text-tinta-media tabular-nums max-sm:block max-sm:text-left sm:px-0 sm:py-4">
        <span className="text-tinta-media sm:hidden">Alta: </span>
        {fechaCorta(vehiculo.creado_en)}
      </td>
      <td className="px-4 py-1 text-right max-sm:block max-sm:text-left sm:px-0 sm:py-3">
        <div className="relative inline-block text-left">
          <button
            type="button"
            aria-label={`Opciones de ${vehiculo.patente}`}
            aria-expanded={menuAbierto}
            aria-haspopup="true"
            onClick={() => {
              setMenuAbierto((abierto) => !abierto);
              setMensajeError("");
            }}
            disabled={enviando}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 disabled:opacity-50 dark:text-slate-400 dark:hover:bg-[#1e2c44] dark:hover:text-white"
          >
            <MoreHorizontal className="size-4" />
          </button>
          {menuAbierto ? (
            <div
              aria-label={`Acciones de ${vehiculo.patente}`}
              className="absolute right-0 z-10 mt-2 w-56 rounded-xl border border-slate-200 bg-white p-2 text-left shadow-lg dark:border-[#1e2c44] dark:bg-[#111c2e]"
            >
              <button
                type="button"
                onClick={() => {
                  setDialogoAbierto(true);
                  setMenuAbierto(false);
                  setMensajeError("");
                }}
                className="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-700 hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-[#16253d]"
              >
                Editar
              </button>
              <button
                type="button"
                onClick={confirmarBaja}
                disabled={enviando}
                className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50 dark:text-red-400 dark:hover:bg-red-950/40"
              >
                <Trash2 className="size-4" />
                Dar de baja
              </button>
              {mensajeError ? (
                <p
                  role="alert"
                  className="px-3 py-2 text-left text-xs text-red-700 dark:text-red-300"
                >
                  {mensajeError}
                </p>
              ) : null}
            </div>
          ) : null}
        </div>
        {dialogoAbierto ? (
          <DialogoVehiculo
            vehiculo={vehiculo}
            tiposVehiculo={tiposVehiculo}
            choferes={choferes}
            onCerrar={() => setDialogoAbierto(false)}
          />
        ) : null}
      </td>
    </tr>
  );
}
