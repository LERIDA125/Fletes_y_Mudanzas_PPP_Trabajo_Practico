"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { MoreHorizontal, Trash2 } from "lucide-react";

import { eliminarChofer } from "@/features/choferes/actions";
import { DialogoConfirmacion } from "@/components/ui/dialogo-confirmacion";
import { useMenuDesplegable } from "@/lib/hooks/use-menu-desplegable";
import { fechaCorta, formatearSaldo } from "@/lib/utils/formato";

import type { Chofer } from "../types";
import { DialogoChofer } from "./dialogo-chofer";

export function FilaChofer({ chofer }: { chofer: Chofer }) {
  const router = useRouter();
  const { abierto, alternar, cerrar, anclaRef, menuRef, estilo } = useMenuDesplegable();
  const [dialogoAbierto, setDialogoAbierto] = useState(false);
  const [confirmacionAbierta, setConfirmacionAbierta] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");

  async function confirmarBaja() {
    setMensajeError("");
    setEnviando(true);
    try {
      const resultado = await eliminarChofer(chofer.id);
      if (!resultado.ok) {
        setConfirmacionAbierta(false);
        setMensajeError(resultado.mensaje);
        return;
      }
      setConfirmacionAbierta(false);
      cerrar();
      router.refresh();
    } finally {
      setEnviando(false);
    }
  }

  return (
    <tr className="border-t border-linea align-top max-sm:block dark:border-[#1e2c44]">
      <th
        scope="row"
        className="px-4 py-4 text-left text-[1rem] font-semibold text-tinta max-sm:block sm:px-0 sm:pr-4 dark:text-white"
      >
        {chofer.nombre_completo}
        <span className="mt-1 block text-[0.875rem] font-normal text-tinta-media dark:text-slate-400">
          {chofer.telefono}
        </span>
      </th>
      <td className="px-4 py-1 text-right text-[0.875rem] text-tinta tabular-nums max-sm:block max-sm:text-left sm:px-0 sm:py-4 sm:pr-4 dark:text-slate-100">
        <span className="text-tinta-media sm:hidden dark:text-slate-400">
          Saldo a favor:{" "}
        </span>
        {formatearSaldo(chofer.saldo_a_favor)}
      </td>
      <td className="px-4 py-1 text-right text-[0.875rem] text-tinta-media tabular-nums max-sm:block max-sm:text-left sm:px-0 sm:py-4 sm:pr-4 dark:text-slate-400">
        <span className="text-tinta-media sm:hidden dark:text-slate-400">Alta: </span>
        {fechaCorta(chofer.creado_en)}
      </td>
      <td className="px-4 py-1 text-right max-sm:block max-sm:text-left sm:px-0 sm:py-3">
        <div ref={anclaRef} className="inline-block text-left">
          <button
            type="button"
            aria-label={`Opciones de ${chofer.nombre_completo}`}
            aria-expanded={abierto}
            aria-haspopup="true"
            onClick={() => {
              alternar();
              setMensajeError("");
            }}
            disabled={enviando}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 disabled:opacity-50 dark:text-slate-400 dark:hover:bg-[#1e2c44] dark:hover:text-white"
          >
            <MoreHorizontal className="size-4" />
          </button>
          {abierto ? (
            <div
              ref={menuRef}
              style={estilo}
              aria-label={`Acciones de ${chofer.nombre_completo}`}
              className="z-50 rounded-xl border border-slate-200 bg-white p-2 text-left shadow-xl dark:border-[#1e2c44] dark:bg-[#111c2e]"
            >
              <button
                type="button"
                onClick={() => {
                  setDialogoAbierto(true);
                  cerrar();
                  setMensajeError("");
                }}
                className="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-700 hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-[#16253d]"
              >
                Editar
              </button>
              <button
                type="button"
                onClick={() => {
                  setConfirmacionAbierta(true);
                  cerrar();
                  setMensajeError("");
                }}
                disabled={enviando}
                className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50 dark:text-red-400 dark:hover:bg-red-950/40"
              >
                <Trash2 className="size-4" />
                Dar de baja
              </button>
            </div>
          ) : null}
          {mensajeError ? (
            <p
              role="alert"
              className="mt-2 block max-w-56 px-2 text-left text-xs text-red-700 dark:text-red-300"
            >
              {mensajeError}
            </p>
          ) : null}
        </div>
        {dialogoAbierto ? (
          <DialogoChofer chofer={chofer} onCerrar={() => setDialogoAbierto(false)} />
        ) : null}
        {confirmacionAbierta ? (
          <DialogoConfirmacion
            titulo="Dar de baja chofer"
            descripcion={`¿Dar de baja a ${chofer.nombre_completo}? Esta acción no se puede deshacer.`}
            textoConfirmar="Sí, dar de baja"
            enviando={enviando}
            onConfirmar={confirmarBaja}
            onCancelar={() => setConfirmacionAbierta(false)}
          />
        ) : null}
      </td>
    </tr>
  );
}
