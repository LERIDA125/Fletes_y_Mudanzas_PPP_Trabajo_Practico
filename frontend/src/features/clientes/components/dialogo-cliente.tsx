"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";

import { guardarCliente } from "@/features/clientes/actions";
import { esquemaCliente, type ValoresCliente } from "@/features/clientes/schemas/cliente";
import type { Cliente } from "@/features/clientes/types";

type Propiedades = {
  cliente?: Cliente;
  onCerrar: () => void;
};

export function DialogoCliente({ cliente, onCerrar }: Propiedades) {
  const router = useRouter();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [mensaje, setMensaje] = useState("");
  const [enviando, setEnviando] = useState(false);
  const editando = cliente !== undefined;
  const sufijoId = cliente?.id ?? "nuevo";

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ValoresCliente>({
    resolver: zodResolver(esquemaCliente),
    defaultValues: {
      razon_social: cliente?.razon_social ?? "",
      telefono: cliente?.telefono ?? "",
      direccion_habitual: cliente?.direccion_habitual ?? "",
      tiene_cuenta_corriente: cliente?.tiene_cuenta_corriente ?? false,
    },
  });

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) {
      dialog.showModal();
    }
  }, []);

  async function guardar(valores: ValoresCliente) {
    setMensaje("");
    setEnviando(true);
    try {
      const respuesta = await guardarCliente(valores, cliente?.id);
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
      aria-labelledby={`titulo-dialogo-cliente-${sufijoId}`}
      className="m-auto max-h-[92dvh] w-[calc(100%-2rem)] max-w-md overflow-y-auto rounded-xl border border-panel-borde/70 bg-panel-superficie p-0 text-panel-texto shadow-2xl backdrop:bg-slate-950/60 backdrop:backdrop-blur-sm"
    >
      <div className="flex items-start justify-between gap-4 border-b border-panel-borde/60 bg-panel-suave/40 px-6 py-5">
        <div>
          <h2
            id={`titulo-dialogo-cliente-${sufijoId}`}
            className="text-lg font-bold text-panel-texto"
          >
            {editando ? "Editar cliente" : "Nuevo cliente"}
          </h2>
          <p className="mt-0.5 text-xs text-panel-secundario">
            {editando
              ? "Actualizá los datos del cliente sin perder su historial."
              : "Registrá un nuevo cliente en el padrón operativo."}
          </p>
        </div>
        <button
          type="button"
          aria-label="Cerrar formulario"
          onClick={onCerrar}
          className="inline-flex size-8 shrink-0 items-center justify-center rounded-lg text-panel-secundario transition-colors hover:bg-panel-suave hover:text-panel-texto focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul"
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

      <form
        className="flex flex-col gap-4 p-6"
        noValidate
        onSubmit={handleSubmit(guardar)}
      >
        <div>
          <label
            htmlFor={`razon_social-${sufijoId}`}
            className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
          >
            Razón social
          </label>
          <input
            id={`razon_social-${sufijoId}`}
            aria-invalid={Boolean(errors.razon_social)}
            aria-describedby={
              errors.razon_social ? `razon_social-error-${sufijoId}` : undefined
            }
            autoComplete="organization"
            {...register("razon_social")}
            className={claseControl}
          />
          {errors.razon_social ? (
            <p id={`razon_social-error-${sufijoId}`} className="mt-1 text-xs text-alerta">
              {errors.razon_social.message}
            </p>
          ) : null}
        </div>

        <div>
          <label
            htmlFor={`telefono-${sufijoId}`}
            className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
          >
            Teléfono
          </label>
          <input
            id={`telefono-${sufijoId}`}
            type="tel"
            inputMode="tel"
            placeholder="351 555 0100"
            aria-invalid={Boolean(errors.telefono)}
            aria-describedby={errors.telefono ? `telefono-error-${sufijoId}` : undefined}
            autoComplete="tel"
            {...register("telefono")}
            className={claseControl}
          />
          {errors.telefono ? (
            <p id={`telefono-error-${sufijoId}`} className="mt-1 text-xs text-alerta">
              {errors.telefono.message}
            </p>
          ) : null}
        </div>

        <div>
          <label
            htmlFor={`direccion_habitual-${sufijoId}`}
            className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
          >
            Dirección habitual
          </label>
          <input
            id={`direccion_habitual-${sufijoId}`}
            aria-invalid={Boolean(errors.direccion_habitual)}
            aria-describedby={
              errors.direccion_habitual
                ? `direccion_habitual-error-${sufijoId}`
                : undefined
            }
            autoComplete="street-address"
            {...register("direccion_habitual")}
            className={claseControl}
          />
          {errors.direccion_habitual ? (
            <p
              id={`direccion_habitual-error-${sufijoId}`}
              className="mt-1 text-xs text-alerta"
            >
              {errors.direccion_habitual.message}
            </p>
          ) : null}
        </div>

        <label
          htmlFor={`tiene_cuenta_corriente-${sufijoId}`}
          className="flex items-center gap-2 text-sm font-medium text-panel-texto"
        >
          <input
            id={`tiene_cuenta_corriente-${sufijoId}`}
            type="checkbox"
            {...register("tiene_cuenta_corriente")}
            className="size-4 rounded border-panel-borde text-panel-azul focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul"
          />
          Tiene cuenta corriente
        </label>

        {mensaje ? (
          <p
            role="alert"
            className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700"
          >
            {mensaje}
          </p>
        ) : null}

        <div className="flex justify-end gap-2 pt-2">
          <button type="button" onClick={onCerrar} className={claseBotonSecundario}>
            Cancelar
          </button>
          <button type="submit" disabled={enviando} className={claseBotonPrincipal}>
            {enviando ? "Guardando…" : editando ? "Guardar cambios" : "Guardar cliente"}
          </button>
        </div>
      </form>
    </dialog>
  );
}

const claseControl =
  "mt-1 block min-h-10 w-full rounded-lg border border-panel-borde/80 bg-white px-3 py-2 text-sm text-panel-texto shadow-xs transition-colors focus:border-panel-azul focus:ring-2 focus:ring-panel-azul/20 focus-visible:outline-none dark:bg-[#0d1626] dark:text-white";

const claseBotonSecundario =
  "inline-flex min-h-10 items-center justify-center rounded-lg border border-panel-borde bg-panel-suave/80 px-4 text-sm font-semibold text-panel-texto transition-all hover:bg-panel-suave focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul";

const claseBotonPrincipal =
  "inline-flex min-h-10 items-center justify-center rounded-lg bg-panel-primario px-4 text-sm font-bold text-white shadow-md transition-all hover:bg-slate-800 active:scale-[0.99] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul disabled:cursor-not-allowed disabled:opacity-50";
