"use client";

import { useEffect, useId, useRef } from "react";

type Propiedades = {
  titulo: string;
  descripcion: string;
  textoConfirmar?: string;
  textoCancelar?: string;
  enviando?: boolean;
  onConfirmar: () => void;
  onCancelar: () => void;
};

/**
 * Confirmación bloqueante para acciones destructivas.
 *
 * Reemplaza a `window.confirm`: se puede estilar, respeta el modo oscuro y es
 * accesible (nombre accesible + foco dentro del diálogo nativo).
 */
export function DialogoConfirmacion({
  titulo,
  descripcion,
  textoConfirmar = "Eliminar",
  textoCancelar = "Cancelar",
  enviando = false,
  onConfirmar,
  onCancelar,
}: Propiedades) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const idTitulo = useId();
  const idDescripcion = useId();

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) {
      dialog.showModal();
    }
  }, []);

  return (
    <dialog
      ref={dialogRef}
      onClose={onCancelar}
      aria-labelledby={idTitulo}
      aria-describedby={idDescripcion}
      className="m-auto max-h-[92dvh] w-[calc(100%-2rem)] max-w-md overflow-y-auto rounded-xl border border-panel-borde/70 bg-panel-superficie p-0 text-panel-texto shadow-2xl backdrop:bg-slate-950/60 backdrop:backdrop-blur-sm"
    >
      <div className="flex flex-col gap-2 border-b border-panel-borde/60 bg-panel-suave/40 px-6 py-5">
        <h2 id={idTitulo} className="text-lg font-bold text-panel-texto">
          {titulo}
        </h2>
        <p id={idDescripcion} className="text-sm text-panel-secundario">
          {descripcion}
        </p>
      </div>

      <div className="flex justify-end gap-2 px-6 py-5">
        <button
          type="button"
          onClick={onCancelar}
          disabled={enviando}
          className="inline-flex min-h-10 items-center justify-center rounded-lg border border-panel-borde bg-panel-suave/80 px-4 text-sm font-semibold text-panel-texto transition-all hover:bg-panel-suave focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul disabled:cursor-not-allowed disabled:opacity-50"
        >
          {textoCancelar}
        </button>
        <button
          type="button"
          onClick={onConfirmar}
          disabled={enviando}
          className="inline-flex min-h-10 items-center justify-center rounded-lg bg-red-600 px-4 text-sm font-bold text-white shadow-md transition-all hover:bg-red-700 active:scale-[0.99] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {enviando ? "Procesando…" : textoConfirmar}
        </button>
      </div>
    </dialog>
  );
}
