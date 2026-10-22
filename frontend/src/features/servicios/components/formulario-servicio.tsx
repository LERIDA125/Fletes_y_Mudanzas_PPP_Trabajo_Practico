"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { useForm, useWatch } from "react-hook-form";

import { registrarServicio, solicitarCotizacion } from "@/features/servicios/actions";
import type {
  ClienteOpcion,
  Cotizacion,
  TipoVehiculoOpcion,
} from "@/features/servicios/types";
import {
  esquemaFormularioServicio,
  type ValoresFormularioServicio,
} from "@/features/servicios/schemas/servicio";

import { ResumenCotizacion } from "./resumen-cotizacion";

const formatoMoneda = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
});

type Propiedades = {
  clientes: ClienteOpcion[];
  tiposVehiculo: TipoVehiculoOpcion[];
};

function fechaLocal(): string {
  const fecha = new Date();
  const anio = fecha.getFullYear();
  const mes = String(fecha.getMonth() + 1).padStart(2, "0");
  const dia = String(fecha.getDate()).padStart(2, "0");
  return `${anio}-${mes}-${dia}`;
}

function cotizacionCoincide(
  cotizacion: Cotizacion,
  valores: Partial<ValoresFormularioServicio>,
): boolean {
  return (
    cotizacion.id_tipo_vehiculo === Number(valores.id_tipo_vehiculo) &&
    Number(cotizacion.horas_estimadas) === Number(valores.horas_estimadas) &&
    Number(cotizacion.distancia_ida_km) === Number(valores.distancia_ida_km)
  );
}

export function FormularioServicio({ clientes, tiposVehiculo }: Propiedades) {
  const router = useRouter();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [cotizacion, setCotizacion] = useState<Cotizacion | null>(null);
  const [mensaje, setMensaje] = useState("");
  const [servicioCreado, setServicioCreado] = useState<string | null>(null);
  const [estaCotizando, setEstaCotizando] = useState(false);
  const [estaRegistrando, setEstaRegistrando] = useState(false);

  const {
    register,
    control,
    getValues,
    trigger,
    reset,
    formState: { errors },
  } = useForm<ValoresFormularioServicio>({
    resolver: zodResolver(esquemaFormularioServicio),
    defaultValues: {
      id_cliente: "",
      id_tipo_vehiculo: "",
      fecha: fechaLocal(),
      hora_inicio: "",
      horas_estimadas: "1",
      distancia_ida_km: "0",
    },
  });

  const valores = useWatch({ control });
  const cotizacionVigente =
    cotizacion !== null && cotizacionCoincide(cotizacion, valores);
  const catalogosDisponibles = clientes.length > 0 && tiposVehiculo.length > 0;

  async function pedirCotizacion() {
    setMensaje("");
    setServicioCreado(null);
    setCotizacion(null);
    if (!(await trigger())) {
      return;
    }

    const actual = getValues();
    setEstaCotizando(true);
    try {
      const respuesta = await solicitarCotizacion({
        id_tipo_vehiculo: Number(actual.id_tipo_vehiculo),
        horas_estimadas: Number(actual.horas_estimadas),
        distancia_ida_km: Number(actual.distancia_ida_km),
      });
      if (respuesta.ok) {
        setCotizacion(respuesta.dato);
        return;
      }
      setMensaje(respuesta.mensaje);
    } finally {
      setEstaCotizando(false);
    }
  }

  async function confirmarYCrear() {
    setMensaje("");
    if (
      !(await trigger()) ||
      !cotizacion ||
      !cotizacionCoincide(cotizacion, getValues())
    ) {
      setMensaje(
        "Revisá los datos y solicitá una cotización vigente antes de registrar.",
      );
      return;
    }

    const actual = getValues();
    setEstaRegistrando(true);
    try {
      const respuesta = await registrarServicio({
        id_cliente: Number(actual.id_cliente),
        id_tipo_vehiculo: Number(actual.id_tipo_vehiculo),
        fecha: actual.fecha,
        hora_inicio: actual.hora_inicio || null,
        horas_estimadas: Number(actual.horas_estimadas),
        distancia_ida_km: Number(actual.distancia_ida_km),
      });
      if (!respuesta.ok) {
        setMensaje(respuesta.mensaje);
        return;
      }

      setServicioCreado(
        `Servicio #${respuesta.dato.id_servicio} registrado. Precio final: ${formatoMoneda.format(
          Number(respuesta.dato.precio_total),
        )}.`,
      );
      setCotizacion(null);
      reset({
        id_cliente: "",
        id_tipo_vehiculo: "",
        fecha: fechaLocal(),
        hora_inicio: "",
        horas_estimadas: "1",
        distancia_ida_km: "0",
      });
      router.refresh();
    } finally {
      setEstaRegistrando(false);
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={() => dialogRef.current?.showModal()}
        className="inline-flex min-h-10 items-center justify-center gap-1.5 rounded-lg bg-[#0b1c30] px-4 py-2 text-sm font-semibold text-white shadow-xs transition-all hover:bg-slate-800 active:scale-[0.99] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul"
      >
        <span className="text-base font-bold leading-none" aria-hidden="true">
          +
        </span>
        <span>Nuevo servicio</span>
      </button>

      <dialog
        ref={dialogRef}
        aria-labelledby="titulo-formulario-servicio"
        className="m-auto max-h-[92dvh] w-[calc(100%-2rem)] max-w-2xl overflow-y-auto rounded-xl border border-panel-borde/70 bg-panel-superficie p-0 text-panel-texto shadow-2xl backdrop:bg-slate-950/60 backdrop:backdrop-blur-sm"
      >
        <div className="flex items-start justify-between gap-4 border-b border-panel-borde/60 bg-panel-suave/40 px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-panel-primario text-white shadow-sm">
              <svg
                className="size-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <div>
              <h2
                id="titulo-formulario-servicio"
                className="text-lg font-bold text-panel-texto"
              >
                Cotizar y registrar un servicio
              </h2>
              <p className="mt-0.5 text-xs text-panel-secundario">
                La cotización oficial se calcula en el servidor con tarifas vigentes.
              </p>
            </div>
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
          className="grid gap-4 p-6 sm:grid-cols-2"
          noValidate
          onSubmit={(evento) => evento.preventDefault()}
        >
          <div className="sm:col-span-2 rounded-lg bg-blue-50/80 border border-blue-100 p-3 text-xs text-blue-900 leading-relaxed">
            Completá los datos del viaje para obtener el importe tarifado oficial. Luego
            podrás confirmar el alta definitiva.
          </div>

          {clientes.length === 0 ? (
            <p role="status" className="text-sm text-panel-secundario sm:col-span-2">
              No hay clientes activos para seleccionar.
            </p>
          ) : (
            <Campo id="id_cliente" etiqueta="Cliente" error={errors.id_cliente?.message}>
              <select
                id="id_cliente"
                aria-invalid={Boolean(errors.id_cliente)}
                aria-describedby={errors.id_cliente ? "id_cliente-error" : undefined}
                {...register("id_cliente")}
                className={claseControl}
              >
                <option value="">Elegí un cliente</option>
                {clientes.map((cliente) => (
                  <option key={cliente.id} value={cliente.id}>
                    {cliente.razon_social}
                  </option>
                ))}
              </select>
            </Campo>
          )}

          {tiposVehiculo.length === 0 ? (
            <p role="status" className="text-sm text-panel-secundario sm:col-span-2">
              No hay tipos de vehículo activos para cotizar.
            </p>
          ) : (
            <Campo
              id="id_tipo_vehiculo"
              etiqueta="Tipo de vehículo"
              error={errors.id_tipo_vehiculo?.message}
            >
              <select
                id="id_tipo_vehiculo"
                aria-invalid={Boolean(errors.id_tipo_vehiculo)}
                aria-describedby={
                  errors.id_tipo_vehiculo ? "id_tipo_vehiculo-error" : undefined
                }
                {...register("id_tipo_vehiculo")}
                className={claseControl}
              >
                <option value="">Elegí un tipo</option>
                {tiposVehiculo.map((tipo) => (
                  <option key={tipo.id} value={tipo.id}>
                    {tipo.descripcion}
                  </option>
                ))}
              </select>
            </Campo>
          )}

          <Campo id="fecha" etiqueta="Fecha" error={errors.fecha?.message}>
            <input
              id="fecha"
              type="date"
              aria-invalid={Boolean(errors.fecha)}
              aria-describedby={errors.fecha ? "fecha-error" : undefined}
              {...register("fecha")}
              className={claseControl}
            />
          </Campo>

          <Campo id="hora_inicio" etiqueta="Hora de inicio (opcional)">
            <input
              id="hora_inicio"
              type="time"
              {...register("hora_inicio")}
              className={claseControl}
            />
          </Campo>

          <Campo
            id="horas_estimadas"
            etiqueta="Horas estimadas"
            error={errors.horas_estimadas?.message}
          >
            <input
              id="horas_estimadas"
              type="number"
              min="1"
              step="0.01"
              inputMode="decimal"
              aria-invalid={Boolean(errors.horas_estimadas)}
              aria-describedby={
                errors.horas_estimadas ? "horas_estimadas-error" : undefined
              }
              {...register("horas_estimadas")}
              className={claseControl}
            />
          </Campo>

          <Campo
            id="distancia_ida_km"
            etiqueta="Distancia de ida (km)"
            error={errors.distancia_ida_km?.message}
          >
            <input
              id="distancia_ida_km"
              type="number"
              min="0"
              step="0.01"
              inputMode="decimal"
              aria-invalid={Boolean(errors.distancia_ida_km)}
              aria-describedby={
                errors.distancia_ida_km ? "distancia_ida_km-error" : undefined
              }
              {...register("distancia_ida_km")}
              className={claseControl}
            />
          </Campo>

          {mensaje ? (
            <p
              role="alert"
              className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm font-medium text-red-700 sm:col-span-2"
            >
              {mensaje}
            </p>
          ) : null}

          {servicioCreado ? (
            <p
              role="status"
              className="rounded-lg bg-emerald-50 border border-emerald-200 px-3 py-2 text-sm font-medium text-emerald-800 sm:col-span-2"
            >
              {servicioCreado}
            </p>
          ) : null}

          <div className="sm:col-span-2 pt-2">
            <button
              type="button"
              disabled={estaCotizando || estaRegistrando || !catalogosDisponibles}
              onClick={pedirCotizacion}
              className={claseBoton}
            >
              {estaCotizando ? "Procesando…" : "Cotizar viaje"}
            </button>
          </div>

          {cotizacion ? (
            <div className="sm:col-span-2 mt-2">
              <ResumenCotizacion cotizacion={cotizacion} vigente={cotizacionVigente} />
              {cotizacionVigente ? (
                <button
                  type="button"
                  disabled={estaRegistrando}
                  onClick={confirmarYCrear}
                  className={`${claseBotonPrincipal} mt-4 w-full`}
                >
                  {estaRegistrando ? "Registrando…" : "Confirmar y registrar servicio"}
                </button>
              ) : null}
            </div>
          ) : null}
        </form>
      </dialog>
    </>
  );
}

const claseControl =
  "mt-1 block min-h-10 w-full rounded-lg border border-panel-borde/80 bg-white px-3 py-2 text-sm text-panel-texto shadow-xs transition-colors focus:border-panel-azul focus:ring-2 focus:ring-panel-azul/20 focus-visible:outline-none";

const claseBoton =
  "inline-flex min-h-10 items-center justify-center rounded-lg border border-panel-borde bg-panel-suave/80 px-4 text-sm font-semibold text-panel-texto transition-all hover:bg-panel-suave hover:border-slate-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul disabled:cursor-not-allowed disabled:opacity-50";

const claseBotonPrincipal =
  "inline-flex min-h-11 items-center justify-center rounded-lg bg-panel-primario px-5 text-sm font-bold text-white shadow-md transition-all hover:bg-slate-800 active:scale-[0.99] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul disabled:cursor-not-allowed disabled:opacity-50";

function Campo({
  id,
  etiqueta,
  error,
  children,
}: {
  id: string;
  etiqueta: string;
  error?: string;
  children: React.ReactNode;
}) {
  const idError = `${id}-error`;
  return (
    <div>
      <label
        htmlFor={id}
        className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
      >
        {etiqueta}
      </label>
      {children}
      {error ? (
        <p id={idError} className="mt-1 text-xs text-alerta">
          {error}
        </p>
      ) : null}
    </div>
  );
}
