"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
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
    <details className="mb-8 border-y border-linea">
      <summary className="cursor-pointer list-none px-4 py-4 text-[1rem] font-semibold text-tinta marker:hidden sm:px-0">
        Nuevo servicio
      </summary>
      <form
        className="grid gap-5 border-t border-linea px-4 py-6 sm:grid-cols-2 sm:px-0"
        noValidate
        onSubmit={(evento) => evento.preventDefault()}
      >
        <div className="sm:col-span-2">
          <p className="text-[0.875rem] text-tinta-media">
            Primero obtené una cotización del servidor. El importe se vuelve a calcular al
            registrar el servicio.
          </p>
        </div>

        {clientes.length === 0 ? (
          <p role="status" className="sm:col-span-2 text-[0.875rem] text-tinta-media">
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
          <p role="status" className="sm:col-span-2 text-[0.875rem] text-tinta-media">
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
            className="sm:col-span-2 text-[0.875rem] font-medium text-alerta"
          >
            {mensaje}
          </p>
        ) : null}
        {servicioCreado ? (
          <p
            role="status"
            className="sm:col-span-2 text-[0.875rem] font-medium text-tinta"
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
    </details>
  );
}

const claseControl =
  "mt-1 block min-h-11 w-full rounded-[4px] border border-linea bg-white px-3 text-[0.9375rem] text-tinta focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-senal";

const claseBoton =
  "inline-flex min-h-11 items-center justify-center rounded-[4px] bg-tinta px-5 text-[0.9375rem] font-semibold text-papel hover:bg-tinta/90 disabled:cursor-not-allowed disabled:opacity-50";

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
      <label htmlFor={id} className="block text-[0.875rem] font-medium text-tinta">
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
