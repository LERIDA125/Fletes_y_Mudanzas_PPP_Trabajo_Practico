"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { MoreHorizontal, Trash2 } from "lucide-react";

import { eliminarCliente } from "@/features/clientes/actions";
import type { Cliente } from "@/features/clientes/types";
import { fechaCorta } from "@/lib/utils/formato";

import { DialogoCliente } from "./dialogo-cliente";

export function FilaCliente({ cliente }: { cliente: Cliente }) {
  const router = useRouter();
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [dialogoAbierto, setDialogoAbierto] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");

  async function confirmarBaja() {
    const confirmado = window.confirm(
      `¿Dar de baja a ${cliente.razon_social}? Esta acción no se puede deshacer.`,
    );
    if (!confirmado) {
      return;
    }

    setMensajeError("");
    setEnviando(true);
    try {
      const resultado = await eliminarCliente(cliente.id);
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
    <tr className="border-t border-linea align-top max-sm:block dark:border-[#1e2c44]">
      <th
        scope="row"
        className="px-4 py-4 text-left text-[1rem] font-semibold text-tinta max-sm:block sm:px-0 sm:pr-4 dark:text-white"
      >
        {cliente.razon_social}
        <span className="mt-1 block text-[0.875rem] font-normal text-tinta-media dark:text-slate-400">
          {cliente.direccion_habitual}
        </span>
      </th>
      <td className="px-4 py-1 text-[0.875rem] text-tinta tabular-nums max-sm:block sm:px-0 sm:py-4 sm:pr-4 dark:text-slate-100">
        <span className="text-tinta-media sm:hidden dark:text-slate-400">Teléfono: </span>
        {cliente.telefono}
      </td>
      <td className="px-4 py-1 text-[0.875rem] text-tinta max-sm:block sm:px-0 sm:py-4 sm:pr-4 dark:text-slate-100">
        <span className="text-tinta-media sm:hidden dark:text-slate-400">
          Cuenta corriente:{" "}
        </span>
        {cliente.tiene_cuenta_corriente ? "Sí" : "No"}
      </td>
      <td className="px-4 py-1 text-right text-[0.875rem] text-tinta-media tabular-nums max-sm:block max-sm:text-left sm:px-0 sm:py-4 dark:text-slate-400">
        <span className="text-tinta-media sm:hidden dark:text-slate-400">Alta: </span>
        {fechaCorta(cliente.creado_en)}
      </td>
      <td className="px-4 py-1 text-right max-sm:block max-sm:text-left sm:px-0 sm:py-3">
        <div className="relative inline-block text-left">
          <button
            type="button"
            aria-label={`Opciones de ${cliente.razon_social}`}
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
              aria-label={`Acciones de ${cliente.razon_social}`}
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
          <DialogoCliente cliente={cliente} onCerrar={() => setDialogoAbierto(false)} />
        ) : null}
      </td>
    </tr>
  );
}
