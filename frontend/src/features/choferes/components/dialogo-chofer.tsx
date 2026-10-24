"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { useForm } from "react-hook-form";

import { guardarChofer } from "@/features/choferes/actions";
import { esquemaChofer, type ValoresChofer } from "@/features/choferes/schemas/chofer";
import type { Chofer } from "@/features/choferes/types";

type Propiedades = {
  chofer?: Chofer;
};

export function DialogoChofer({ chofer }: Propiedades) {
  const router = useRouter();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [mensaje, setMensaje] = useState("");
  const [enviando, setEnviando] = useState(false);
  const editando = chofer !== undefined;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ValoresChofer>({
    resolver: zodResolver(esquemaChofer),
    defaultValues: {
      nombre_completo: chofer?.nombre_completo ?? "",
      telefono: chofer?.telefono ?? "",
    },
  });

  function abrir() {
    setMensaje("");
    if (editando) {
      reset({
        nombre_completo: chofer.nombre_completo,
        telefono: chofer.telefono,
      });
    }
    dialogRef.current?.showModal();
  }

  async function guardar(valores: ValoresChofer) {
    setMensaje("");
    setEnviando(true);
    try {
      const respuesta = await guardarChofer(valores, chofer?.id);
      if (!respuesta.ok) {
        setMensaje(respuesta.mensaje);
        return;
      }
      dialogRef.current?.close();
      if (!editando) {
        reset({ nombre_completo: "", telefono: "" });
      }
      router.refresh();
    } finally {
      setEnviando(false);
    }
  }

  return (
    <>
      {editando ? (
        <button
          type="button"
          onClick={abrir}
          aria-label={`Editar a ${chofer.nombre_completo}`}
          className="inline-flex min-h-8 items-center justify-center rounded-lg border border-panel-borde/70 bg-white px-2.5 text-xs font-semibold text-panel-texto transition-colors hover:bg-panel-suave/70 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white dark:hover:bg-[#16253d]"
        >
          Editar
        </button>
      ) : (
        <button
          type="button"
          onClick={abrir}
          className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-orange-200 transition-all hover:bg-orange-600 active:scale-[0.99] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500"
        >
          <span className="text-base font-bold leading-none" aria-hidden="true">
            +
          </span>
          <span>Nuevo chofer</span>
        </button>
      )}

      <dialog
        ref={dialogRef}
        aria-labelledby={`titulo-dialogo-chofer-${chofer?.id ?? "nuevo"}`}
        className="m-auto max-h-[92dvh] w-[calc(100%-2rem)] max-w-md overflow-y-auto rounded-xl border border-panel-borde/70 bg-panel-superficie p-0 text-panel-texto shadow-2xl backdrop:bg-slate-950/60 backdrop:backdrop-blur-sm"
      >
        <div className="flex items-start justify-between gap-4 border-b border-panel-borde/60 bg-panel-suave/40 px-6 py-5">
          <div>
            <h2
              id={`titulo-dialogo-chofer-${chofer?.id ?? "nuevo"}`}
              className="text-lg font-bold text-panel-texto"
            >
              {editando ? "Editar chofer" : "Nuevo chofer"}
            </h2>
            <p className="mt-0.5 text-xs text-panel-secundario">
              {editando
                ? "Actualizá los datos de contacto del chofer."
                : "Agregá un chofer al equipo operativo."}
            </p>
          </div>
          <button
            type="button"
            aria-label="Cerrar formulario"
            onClick={() => dialogRef.current?.close()}
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
              htmlFor={`nombre_completo-${chofer?.id ?? "nuevo"}`}
              className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
            >
              Nombre completo
            </label>
            <input
              id={`nombre_completo-${chofer?.id ?? "nuevo"}`}
              aria-invalid={Boolean(errors.nombre_completo)}
              aria-describedby={
                errors.nombre_completo
                  ? `nombre_completo-error-${chofer?.id ?? "nuevo"}`
                  : undefined
              }
              autoComplete="name"
              {...register("nombre_completo")}
              className={claseControl}
            />
            {errors.nombre_completo ? (
              <p
                id={`nombre_completo-error-${chofer?.id ?? "nuevo"}`}
                className="mt-1 text-xs text-alerta"
              >
                {errors.nombre_completo.message}
              </p>
            ) : null}
          </div>

          <div>
            <label
              htmlFor={`telefono-${chofer?.id ?? "nuevo"}`}
              className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
            >
              Teléfono
            </label>
            <input
              id={`telefono-${chofer?.id ?? "nuevo"}`}
              type="tel"
              inputMode="tel"
              placeholder="351 555 0100"
              aria-invalid={Boolean(errors.telefono)}
              aria-describedby={
                errors.telefono ? `telefono-error-${chofer?.id ?? "nuevo"}` : undefined
              }
              autoComplete="tel"
              {...register("telefono")}
              className={claseControl}
            />
            {errors.telefono ? (
              <p
                id={`telefono-error-${chofer?.id ?? "nuevo"}`}
                className="mt-1 text-xs text-alerta"
              >
                {errors.telefono.message}
              </p>
            ) : null}
          </div>

          {mensaje ? (
            <p
              role="alert"
              className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700"
            >
              {mensaje}
            </p>
          ) : null}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => dialogRef.current?.close()}
              className={claseBotonSecundario}
            >
              Cancelar
            </button>
            <button type="submit" disabled={enviando} className={claseBotonPrincipal}>
              {enviando ? "Guardando…" : editando ? "Guardar cambios" : "Crear chofer"}
            </button>
          </div>
        </form>
      </dialog>
    </>
  );
}

const claseControl =
  "mt-1 block min-h-10 w-full rounded-lg border border-panel-borde/80 bg-white px-3 py-2 text-sm text-panel-texto shadow-xs transition-colors focus:border-panel-azul focus:ring-2 focus:ring-panel-azul/20 focus-visible:outline-none dark:bg-[#0d1626] dark:text-white";

const claseBotonSecundario =
  "inline-flex min-h-10 items-center justify-center rounded-lg border border-panel-borde bg-panel-suave/80 px-4 text-sm font-semibold text-panel-texto transition-all hover:bg-panel-suave focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul";

const claseBotonPrincipal =
  "inline-flex min-h-10 items-center justify-center rounded-lg bg-panel-primario px-4 text-sm font-bold text-white shadow-md transition-all hover:bg-slate-800 active:scale-[0.99] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul disabled:cursor-not-allowed disabled:opacity-50";
