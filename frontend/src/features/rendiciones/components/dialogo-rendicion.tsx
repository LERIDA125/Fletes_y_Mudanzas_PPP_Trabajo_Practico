"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";

import { guardarRendicion } from "@/features/rendiciones/actions";
import {
  esquemaRendicion,
  type ValoresRendicion,
} from "@/features/rendiciones/schemas/rendicion";
import type { NuevaRendicion, ServicioElegible } from "@/features/rendiciones/types";
import { formatearFecha, formatearMonto } from "@/features/rendiciones/utils";

export function DialogoRendicion({
  servicios,
  onCerrar,
}: {
  servicios: ServicioElegible[];
  onCerrar: () => void;
}) {
  const router = useRouter();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [mensaje, setMensaje] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [idSeleccionado, setIdSeleccionado] = useState(servicios[0]?.id_servicio ?? 0);
  const primerServicio = servicios[0];

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<ValoresRendicion>({
    resolver: zodResolver(esquemaRendicion),
    defaultValues: {
      id_servicio: primerServicio?.id_servicio ?? 0,
      tarifa: Number(primerServicio?.precio_total ?? 0),
      adelanto: 0,
      combustible: 0,
      peajes: 0,
      otros: 0,
      observaciones: "",
    },
  });

  const servicioSeleccionado = servicios.find(
    (servicio) => servicio.id_servicio === Number(idSeleccionado),
  );

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) {
      dialog.showModal();
    }
  }, []);

  function alCambiarServicio(evento: React.ChangeEvent<HTMLSelectElement>) {
    const id = Number(evento.target.value);
    const servicio = servicios.find((item) => item.id_servicio === id);
    setIdSeleccionado(id);
    setValue("id_servicio", id, { shouldValidate: true });
    if (servicio) {
      setValue("tarifa", Number(servicio.precio_total), { shouldValidate: true });
    }
  }

  async function guardar(valores: ValoresRendicion) {
    setMensaje("");
    setEnviando(true);
    try {
      const datos: NuevaRendicion = {
        id_servicio: valores.id_servicio,
        tarifa: valores.tarifa,
        adelanto: valores.adelanto,
        gastos_informados: {
          combustible: valores.combustible,
          peajes: valores.peajes,
          otros: valores.otros,
        },
        observaciones: valores.observaciones.trim() || null,
      };
      const respuesta = await guardarRendicion(datos);
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
      aria-labelledby="titulo-dialogo-rendicion"
      className="m-auto max-h-[92dvh] w-[calc(100%-2rem)] max-w-lg overflow-y-auto rounded-2xl border border-[#e8edf4] bg-white p-0 text-[#172b4d] shadow-2xl backdrop:bg-[#172b4d]/40 backdrop:backdrop-blur-xs dark:border-[#1e2c44] dark:bg-[#111c2e] dark:text-white"
    >
      <div className="flex items-start justify-between border-b border-[#edf0f4] px-6 py-5 dark:border-[#1e2c44]">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
            Arqueo de caja
          </p>
          <h2 id="titulo-dialogo-rendicion" className="mt-1 text-lg font-bold">
            Registrar nueva rendición
          </h2>
          <p className="mt-0.5 text-xs text-[#8b99ab] dark:text-[#94a3b8]">
            Ingresá la liquidación entregada por el chofer al finalizar el servicio.
          </p>
        </div>
        <button
          type="button"
          aria-label="Cerrar formulario"
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

      <form
        className="flex flex-col gap-4 px-6 py-5 text-xs"
        noValidate
        onSubmit={handleSubmit(guardar)}
      >
        {servicios.length === 0 ? (
          <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-medium text-amber-800 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-300">
            No hay servicios finalizados con chofer sin rendición. Cerrá un servicio para
            poder rendirlo.
          </p>
        ) : null}

        <div>
          <label
            htmlFor="rendicion-servicio"
            className="block font-semibold text-[#62738a] dark:text-[#94a3b8]"
          >
            Servicio finalizado
          </label>
          <select
            id="rendicion-servicio"
            aria-invalid={Boolean(errors.id_servicio)}
            {...register("id_servicio", {
              valueAsNumber: true,
              onChange: alCambiarServicio,
            })}
            className={claseControl}
          >
            {servicios.length === 0 ? (
              <option value={0}>Sin servicios disponibles</option>
            ) : null}
            {servicios.map((servicio) => (
              <option key={servicio.id_servicio} value={servicio.id_servicio}>
                SRV-{servicio.id_servicio} · {servicio.razon_social_cliente} ·{" "}
                {servicio.nombre_chofer}
              </option>
            ))}
          </select>
          {errors.id_servicio ? (
            <p className="mt-1 text-xs text-red-600 dark:text-red-400">
              {errors.id_servicio.message}
            </p>
          ) : null}
        </div>

        {servicioSeleccionado ? (
          <div className="grid grid-cols-2 gap-3 rounded-xl border border-[#e8edf4] bg-[#f8fbff] p-3 dark:border-[#1e2c44] dark:bg-[#0d1626]">
            <p className="text-[#62738a] dark:text-[#94a3b8]">
              Fecha:{" "}
              <span className="font-semibold text-[#172b4d] dark:text-white">
                {formatearFecha(servicioSeleccionado.fecha)}
              </span>
            </p>
            <p className="text-[#62738a] dark:text-[#94a3b8]">
              Precio del servicio:{" "}
              <span className="font-semibold text-[#172b4d] dark:text-white">
                {formatearMonto(servicioSeleccionado.precio_total)}
              </span>
            </p>
          </div>
        ) : null}

        <div className="grid gap-3 sm:grid-cols-2">
          <CampoImporte
            id="rendicion-tarifa"
            etiqueta="Tarifa acordada"
            error={errors.tarifa?.message}
            {...register("tarifa", { valueAsNumber: true })}
          />
          <CampoImporte
            id="rendicion-adelanto"
            etiqueta="Adelanto previo"
            error={errors.adelanto?.message}
            {...register("adelanto", { valueAsNumber: true })}
          />
        </div>

        <fieldset className="rounded-xl border border-[#edf0f4] p-3 dark:border-[#1e2c44]">
          <legend className="px-1 font-semibold text-[#62738a] dark:text-[#94a3b8]">
            Gastos informados
          </legend>
          <div className="grid gap-3 sm:grid-cols-3">
            <CampoImporte
              id="rendicion-combustible"
              etiqueta="Combustible"
              error={errors.combustible?.message}
              {...register("combustible", { valueAsNumber: true })}
            />
            <CampoImporte
              id="rendicion-peajes"
              etiqueta="Peajes"
              error={errors.peajes?.message}
              {...register("peajes", { valueAsNumber: true })}
            />
            <CampoImporte
              id="rendicion-otros"
              etiqueta="Otros"
              error={errors.otros?.message}
              {...register("otros", { valueAsNumber: true })}
            />
          </div>
        </fieldset>

        <div>
          <label
            htmlFor="rendicion-observaciones"
            className="block font-semibold text-[#62738a] dark:text-[#94a3b8]"
          >
            Observaciones (opcional)
          </label>
          <textarea
            id="rendicion-observaciones"
            rows={2}
            placeholder="Detallar comprobantes y gastos..."
            aria-invalid={Boolean(errors.observaciones)}
            {...register("observaciones")}
            className={`${claseControl} resize-none`}
          />
          {errors.observaciones ? (
            <p className="mt-1 text-xs text-red-600 dark:text-red-400">
              {errors.observaciones.message}
            </p>
          ) : null}
        </div>

        {mensaje ? (
          <p
            role="alert"
            className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300"
          >
            {mensaje}
          </p>
        ) : null}

        <div className="flex justify-end gap-2 border-t border-[#edf0f4] pt-4 dark:border-[#1e2c44]">
          <button type="button" onClick={onCerrar} className={claseBotonSecundario}>
            Cancelar
          </button>
          <button
            type="submit"
            disabled={enviando || servicios.length === 0}
            className={claseBotonPrincipal}
          >
            {enviando ? "Guardando…" : "Guardar rendición"}
          </button>
        </div>
      </form>
    </dialog>
  );
}

function CampoImporte({
  id,
  etiqueta,
  error,
  ...propiedades
}: {
  id: string;
  etiqueta: string;
  error?: string;
} & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <div>
      <label
        htmlFor={id}
        className="block font-semibold text-[#62738a] dark:text-[#94a3b8]"
      >
        {etiqueta}
      </label>
      <input
        id={id}
        type="number"
        min="0"
        step="0.01"
        inputMode="decimal"
        aria-invalid={Boolean(error)}
        className={claseControl}
        {...propiedades}
      />
      {error ? (
        <p className="mt-1 text-xs text-red-600 dark:text-red-400">{error}</p>
      ) : null}
    </div>
  );
}

const claseControl =
  "mt-1.5 block min-h-10 w-full rounded-lg border border-[#dfe6ef] bg-white px-3 py-2 text-xs text-[#172b4d] outline-none transition-colors focus:border-[#2165d5] focus:ring-2 focus:ring-[#2165d5]/20 dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white";

const claseBotonSecundario =
  "rounded-lg border border-[#dfe6ef] px-4 py-2 text-xs font-semibold text-[#62738a] hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:text-[#94a3b8] dark:hover:bg-[#16253d]";

const claseBotonPrincipal =
  "rounded-lg bg-[#2165d5] px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-[#1857bd] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-[#2563eb] dark:hover:bg-[#1d4ed8]";
