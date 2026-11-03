"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { cambiarEstado } from "@/features/rendiciones/actions";
import { EtiquetaEstadoRendicion } from "@/features/rendiciones/components/estado-rendicion";
import type { Rendicion } from "@/features/rendiciones/types";
import { formatearFecha, formatearMonto } from "@/features/rendiciones/utils";

export function DialogoDetalleRendicion({
  rendicion,
  onCerrar,
}: {
  rendicion: Rendicion;
  onCerrar: () => void;
}) {
  const router = useRouter();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [mensaje, setMensaje] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) {
      dialog.showModal();
    }
  }, []);

  async function aprobar() {
    setMensaje("");
    setEnviando(true);
    try {
      const respuesta = await cambiarEstado(rendicion.id, "aprobada");
      if (!respuesta.ok) {
        setMensaje(respuesta.mensaje);
        return;
      }
      onCerrar();
      router.refresh();
    } finally {
      setEnviando(false);
    }
  }

  return (
    <dialog
      ref={dialogRef}
      onClose={onCerrar}
      aria-labelledby={`titulo-detalle-rendicion-${rendicion.id}`}
      className="m-auto max-h-[92dvh] w-[calc(100%-2rem)] max-w-lg overflow-y-auto rounded-2xl border border-[#e8edf4] bg-white p-0 text-[#172b4d] shadow-2xl backdrop:bg-[#172b4d]/40 backdrop:backdrop-blur-xs dark:border-[#1e2c44] dark:bg-[#111c2e] dark:text-white"
    >
      <div className="flex items-start justify-between border-b border-[#edf0f4] px-6 py-5 dark:border-[#1e2c44]">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
            Liquidación de viaje
          </p>
          <h2
            id={`titulo-detalle-rendicion-${rendicion.id}`}
            className="mt-1 text-lg font-bold"
          >
            Detalle de rendición {rendicion.codigo}
          </h2>
          <p className="mt-0.5 text-xs text-[#8b99ab] dark:text-[#94a3b8]">
            {rendicion.nombre_chofer} · {formatearFecha(rendicion.fecha)}
          </p>
        </div>
        <button
          type="button"
          aria-label="Cerrar detalle"
          onClick={onCerrar}
          className="rounded-lg p-1.5 text-[#8b99ab] hover:bg-[#f3f5f8] dark:hover:bg-[#18263d]"
        >
          <svg
            aria-hidden="true"
            className="size-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path strokeLinecap="round" d="m6 6 12 12M18 6 6 18" />
          </svg>
        </button>
      </div>

      <div className="flex flex-col gap-4 px-6 py-5 text-xs">
        <div className="flex items-center justify-between gap-3">
          <p className="font-semibold text-[#172b4d] dark:text-white">
            {rendicion.razon_social_cliente}
          </p>
          <EtiquetaEstadoRendicion estado={rendicion.estado} />
        </div>

        <div className="rounded-xl border border-[#e8edf4] bg-[#f8fbff] p-4 dark:border-[#1e2c44] dark:bg-[#0d1626]">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <span className="text-[#8b99ab] dark:text-[#64748b]">Tarifa acordada:</span>
              <p className="text-sm font-bold">{formatearMonto(rendicion.tarifa)}</p>
            </div>
            <div>
              <span className="text-[#8b99ab] dark:text-[#64748b]">
                Adelanto entregado:
              </span>
              <p className="text-sm font-bold">{formatearMonto(rendicion.adelanto)}</p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-[#edf0f4] p-4 dark:border-[#1e2c44] dark:bg-[#0d1626]">
          <p className="font-semibold">Gastos informados:</p>
          <dl className="mt-2 grid grid-cols-3 gap-3 text-[#62738a] dark:text-[#94a3b8]">
            <div>
              <dt>Combustible</dt>
              <dd className="mt-0.5 font-semibold text-[#172b4d] dark:text-white">
                {formatearMonto(rendicion.gastos_informados.combustible)}
              </dd>
            </div>
            <div>
              <dt>Peajes</dt>
              <dd className="mt-0.5 font-semibold text-[#172b4d] dark:text-white">
                {formatearMonto(rendicion.gastos_informados.peajes)}
              </dd>
            </div>
            <div>
              <dt>Otros</dt>
              <dd className="mt-0.5 font-semibold text-[#172b4d] dark:text-white">
                {formatearMonto(rendicion.gastos_informados.otros)}
              </dd>
            </div>
          </dl>

          <div className="mt-3 flex items-center justify-between border-t border-[#edf0f4] pt-3 font-semibold dark:border-[#1e2c44]">
            <span>Total de gastos:</span>
            <span>{formatearMonto(rendicion.gastos_total)}</span>
          </div>
          <div className="mt-2 flex items-center justify-between font-semibold">
            <span>Saldo a liquidar al chofer:</span>
            <span className="text-sm font-bold text-[#2165d5] dark:text-[#60a5fa]">
              {formatearMonto(rendicion.saldo)}
            </span>
          </div>
        </div>

        {rendicion.observaciones ? (
          <div className="rounded-xl border border-[#edf0f4] p-4 dark:border-[#1e2c44]">
            <p className="font-semibold">Observaciones:</p>
            <p className="mt-1 text-[#62738a] dark:text-[#94a3b8]">
              {rendicion.observaciones}
            </p>
          </div>
        ) : null}

        {mensaje ? (
          <p
            role="alert"
            className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300"
          >
            {mensaje}
          </p>
        ) : null}
      </div>

      <div className="flex justify-end gap-2 border-t border-[#edf0f4] px-6 py-4 dark:border-[#1e2c44]">
        <button
          type="button"
          onClick={onCerrar}
          className="rounded-lg border border-[#dfe6ef] px-4 py-2 text-xs font-semibold text-[#62738a] hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:text-[#94a3b8] dark:hover:bg-[#16253d]"
        >
          Cerrar
        </button>
        {rendicion.estado !== "aprobada" ? (
          <button
            type="button"
            onClick={aprobar}
            disabled={enviando}
            className="rounded-lg bg-[#248952] px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-[#1e7244] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {enviando ? "Aprobando…" : "Aprobar rendición"}
          </button>
        ) : null}
      </div>
    </dialog>
  );
}
