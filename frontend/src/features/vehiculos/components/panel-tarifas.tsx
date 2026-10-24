"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { guardarTarifasTipo } from "@/features/vehiculos/actions";
import {
  esquemaTarifasTipo,
  type ValoresTarifasTipo,
} from "@/features/vehiculos/schemas/vehiculo";
import type { TipoVehiculo } from "@/features/vehiculos/types";

const formatoMoneda = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
  maximumFractionDigits: 2,
});

export function PanelTarifas({ tipos }: { tipos: TipoVehiculo[] }) {
  return (
    <section className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm sm:p-6 dark:border-[#1e2c44] dark:bg-[#111c2e]">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-[#172b4d] dark:text-white">
            Tarifas por tipo de vehículo
          </h3>
          <p className="mt-0.5 text-xs text-[#96a2b2] dark:text-[#94a3b8]">
            El servidor usa estos valores para cotizar cada servicio.
          </p>
        </div>
        <span className="rounded-full bg-[#f4f8ff] px-3 py-1 text-xs font-semibold text-[#2165d5] dark:bg-[#16253d] dark:text-[#60a5fa]">
          Vigentes para el cotizador
        </span>
      </div>

      {tipos.length === 0 ? (
        <p role="status" className="mt-4 text-sm text-[#96a2b2] dark:text-[#94a3b8]">
          Todavía no hay tipos de vehículo activos. Creá uno para poder cargar vehículos y
          cotizar.
        </p>
      ) : (
        <div className="mt-4 grid gap-3 lg:grid-cols-2">
          {tipos.map((tipo) => (
            <FormularioTarifa key={tipo.id} tipo={tipo} />
          ))}
        </div>
      )}
    </section>
  );
}

function FormularioTarifa({ tipo }: { tipo: TipoVehiculo }) {
  const router = useRouter();
  const [mensaje, setMensaje] = useState("");
  const [exito, setExito] = useState("");
  const [enviando, setEnviando] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ValoresTarifasTipo>({
    resolver: zodResolver(esquemaTarifasTipo),
    defaultValues: {
      descripcion: tipo.descripcion,
      capacidad_carga_kg: String(tipo.capacidad_carga_kg),
      tarifa_hora_base: String(tipo.tarifa_hora_base),
      tarifa_km_excedente: String(tipo.tarifa_km_excedente),
    },
  });

  async function guardar(valores: ValoresTarifasTipo) {
    setMensaje("");
    setExito("");
    setEnviando(true);
    try {
      const respuesta = await guardarTarifasTipo(tipo.id, {
        descripcion: valores.descripcion,
        capacidad_carga_kg: Number(valores.capacidad_carga_kg),
        tarifa_hora_base: Number(valores.tarifa_hora_base),
        tarifa_km_excedente: Number(valores.tarifa_km_excedente),
      });
      if (!respuesta.ok) {
        setMensaje(respuesta.mensaje);
        return;
      }
      setExito("Tarifas guardadas.");
      router.refresh();
    } finally {
      setEnviando(false);
    }
  }

  const sufijo = `tipo-${tipo.id}`;

  return (
    <form
      noValidate
      onSubmit={handleSubmit(guardar)}
      className="rounded-xl border border-[#edf0f4] bg-[#fbfcfd] p-4 dark:border-[#1e2c44] dark:bg-[#0d1626]"
    >
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-bold text-[#172b4d] dark:text-white">
          {tipo.descripcion}
        </p>
        <p className="text-[11px] text-[#96a2b2] dark:text-[#94a3b8]">
          {formatoMoneda.format(Number(tipo.tarifa_hora_base))} / hora
        </p>
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <div>
          <label
            htmlFor={`capacidad-${sufijo}`}
            className="block text-[11px] font-semibold uppercase tracking-wider text-[#8492a6] dark:text-[#94a3b8]"
          >
            Capacidad (kg)
          </label>
          <input
            id={`capacidad-${sufijo}`}
            type="number"
            min="0"
            step="0.01"
            inputMode="decimal"
            aria-invalid={Boolean(errors.capacidad_carga_kg)}
            {...register("capacidad_carga_kg")}
            className={claseCampo}
          />
          {errors.capacidad_carga_kg ? (
            <p className="mt-1 text-[11px] text-alerta">
              {errors.capacidad_carga_kg.message}
            </p>
          ) : null}
        </div>

        <div>
          <label
            htmlFor={`tarifa-hora-${sufijo}`}
            className="block text-[11px] font-semibold uppercase tracking-wider text-[#8492a6] dark:text-[#94a3b8]"
          >
            Tarifa por hora (ARS)
          </label>
          <input
            id={`tarifa-hora-${sufijo}`}
            type="number"
            min="0"
            step="0.01"
            inputMode="decimal"
            aria-invalid={Boolean(errors.tarifa_hora_base)}
            {...register("tarifa_hora_base")}
            className={claseCampo}
          />
          {errors.tarifa_hora_base ? (
            <p className="mt-1 text-[11px] text-alerta">
              {errors.tarifa_hora_base.message}
            </p>
          ) : null}
        </div>

        <div className="sm:col-span-2">
          <label
            htmlFor={`tarifa-km-${sufijo}`}
            className="block text-[11px] font-semibold uppercase tracking-wider text-[#8492a6] dark:text-[#94a3b8]"
          >
            Tarifa por km excedente (ARS)
          </label>
          <input
            id={`tarifa-km-${sufijo}`}
            type="number"
            min="0"
            step="0.01"
            inputMode="decimal"
            aria-invalid={Boolean(errors.tarifa_km_excedente)}
            {...register("tarifa_km_excedente")}
            className={claseCampo}
          />
          {errors.tarifa_km_excedente ? (
            <p className="mt-1 text-[11px] text-alerta">
              {errors.tarifa_km_excedente.message}
            </p>
          ) : null}
        </div>
      </div>

      <input type="hidden" {...register("descripcion")} />

      {mensaje ? (
        <p role="alert" className="mt-2 text-xs font-medium text-alerta">
          {mensaje}
        </p>
      ) : null}
      {exito ? (
        <p
          role="status"
          className="mt-2 text-xs font-medium text-[#248952] dark:text-[#4ade80]"
        >
          {exito}
        </p>
      ) : null}

      <div className="mt-3 flex justify-end">
        <button
          type="submit"
          disabled={enviando}
          className="inline-flex min-h-8 items-center justify-center rounded-lg bg-[#2165d5] px-3 text-xs font-bold text-white transition-colors hover:bg-[#1857bd] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2165d5] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-[#2563eb] dark:hover:bg-[#1d4ed8]"
        >
          {enviando ? "Guardando…" : "Guardar tarifas"}
        </button>
      </div>
    </form>
  );
}

const claseCampo =
  "mt-1 block min-h-9 w-full rounded-lg border border-[#dfe6ef] bg-white px-2.5 py-1.5 text-xs text-[#172b4d] outline-none focus:border-[#2165d5] dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white";
