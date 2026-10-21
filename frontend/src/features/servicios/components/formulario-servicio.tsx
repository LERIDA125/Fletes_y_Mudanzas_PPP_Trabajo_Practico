"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useRef, useState, useTransition } from "react";
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
  const [estaPendiente, iniciarTransicion] = useTransition();
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
    iniciarTransicion(async () => {
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
    });
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
    iniciarTransicion(async () => {
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
    });
  }

  return (
    <>
      <button
        type="button"
        onClick={() => dialogRef.current?.showModal()}
        className="inline-flex min-h-10 items-center justify-center gap-2 rounded-md bg-panel-primario px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-panel-texto focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul"
      >
        <svg aria-hidden="true" className="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" d="M12 5v14m-7-7h14" />
        </svg>
        <span>Nuevo servicio</span>
      </button>
      <dialog
        ref={dialogRef}
        aria-labelledby="titulo-formulario-servicio"
        className="m-auto max-h-[90dvh] w-[calc(100%-2rem)] max-w-2xl overflow-y-auto rounded-lg border border-panel-borde bg-panel-superficie p-0 text-panel-texto shadow-2xl backdrop:bg-slate-900/50"
      >
        <div className="flex items-start justify-between gap-4 border-b border-panel-borde bg-panel-superficie px-5 py-4 sm:px-6">
          <div>
            <h2 id="titulo-formulario-servicio" className="text-lg font-semibold">
              Cotizar y registrar un servicio
            </h2>
            <p className="mt-1 text-sm text-panel-secundario">
              La cotización se calcula en el servidor y se confirma antes del alta.
            </p>
          </div>
          <button
            type="button"
            aria-label="Cerrar formulario"
            onClick={() => dialogRef.current?.close()}
            className="inline-flex size-9 shrink-0 items-center justify-center rounded-md text-panel-secundario hover:bg-panel-suave hover:text-panel-texto focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul"
          >
            <svg aria-hidden="true" className="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" d="m6 6 12 12M18 6 6 18" />
            </svg>
          </button>
        </div>
        <form
          className="grid gap-4 p-5 sm:grid-cols-2 sm:p-6"
          noValidate
          onSubmit={(evento) => evento.preventDefault()}
        >
          <div className="sm:col-span-2">
            <p className="text-sm text-panel-secundario">
              Primero obtené una cotización del servidor. El importe se vuelve a calcular al
              registrar el servicio.
            </p>
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
            className="text-sm font-medium text-red-700 sm:col-span-2"
          >
            {mensaje}
          </p>
        ) : null}
        {servicioCreado ? (
          <p
            role="status"
            className="text-sm font-medium text-panel-verde sm:col-span-2"
          >
            {servicioCreado}
          </p>
        ) : null}

        <div className="sm:col-span-2">
          <button
            type="button"
            disabled={estaPendiente || !catalogosDisponibles}
            onClick={pedirCotizacion}
            className={claseBoton}
          >
            {estaPendiente ? "Procesando…" : "Cotizar viaje"}
          </button>
        </div>

        {cotizacion ? (
          <div className="sm:col-span-2">
            <ResumenCotizacion cotizacion={cotizacion} vigente={cotizacionVigente} />
            {cotizacionVigente ? (
              <button
                type="button"
                disabled={estaPendiente}
                onClick={confirmarYCrear}
                className={`${claseBoton} mt-4`}
              >
                {estaPendiente ? "Registrando…" : "Confirmar y registrar servicio"}
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
  "mt-1 block min-h-11 w-full rounded-md border border-panel-borde bg-panel-superficie px-3 text-sm text-panel-texto focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul";

const claseBoton =
  "inline-flex min-h-10 items-center justify-center rounded-md bg-panel-primario px-4 text-sm font-semibold text-white transition-colors hover:bg-panel-texto focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul disabled:cursor-not-allowed disabled:opacity-50";

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
      <label htmlFor={id} className="block text-sm font-medium text-panel-secundario">
        {etiqueta}
      </label>
      {children}
      {error ? (
        <p id={idError} className="mt-1 text-[0.8125rem] text-alerta">
          {error}
        </p>
      ) : null}
    </div>
  );
}
