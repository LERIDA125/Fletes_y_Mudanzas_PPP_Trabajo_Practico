"use server";

import { revalidatePath } from "next/cache";

import type {
  AltaServicio,
  ClienteOpcion,
  ConsultaDisponibilidad,
  Cotizacion,
  Disponibilidad,
  Servicio,
  SolicitudCotizacion,
  TipoVehiculoOpcion,
} from "@/features/servicios/types";
import {
  consultarDisponibilidad,
  crearServicio,
  cotizarServicio,
  listarClientesParaAlta,
  listarTiposParaAlta,
} from "@/lib/api/servicios";
import { ErrorApi } from "@/lib/api/http";

export type ResultadoAccion<T> = { ok: true; dato: T } | { ok: false; mensaje: string };

export type CatalogosServicio = {
  clientes: ClienteOpcion[];
  tiposVehiculo: TipoVehiculoOpcion[];
};

/**
 * Catálogos que necesita el alta de servicio. Se piden recién cuando el modal
 * se abre para que el botón de la página se renderice al instante, sin esperar
 * a la API ni quedar oculto si ésta falla.
 */
export async function obtenerCatalogosServicio(): Promise<
  ResultadoAccion<CatalogosServicio>
> {
  try {
    const [clientes, tiposVehiculo] = await Promise.all([
      listarClientesParaAlta(),
      listarTiposParaAlta(),
    ]);
    return { ok: true, dato: { clientes, tiposVehiculo } };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error.clase, "catalogos") };
    }
    throw error;
  }
}

export async function solicitarCotizacion(
  solicitud: SolicitudCotizacion,
): Promise<ResultadoAccion<Cotizacion>> {
  try {
    return { ok: true, dato: await cotizarServicio(solicitud) };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error.clase, "cotizar") };
    }
    throw error;
  }
}

export async function consultarDisponibilidadServicio(
  consulta: ConsultaDisponibilidad,
): Promise<ResultadoAccion<Disponibilidad>> {
  try {
    return { ok: true, dato: await consultarDisponibilidad(consulta) };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error.clase, "disponibilidad") };
    }
    throw error;
  }
}

export async function registrarServicio(
  solicitud: AltaServicio,
): Promise<ResultadoAccion<Servicio>> {
  try {
    const servicio = await crearServicio(solicitud);
    revalidatePath("/servicios");
    revalidatePath("/clientes");
    revalidatePath("/agenda");
    revalidatePath("/");
    return { ok: true, dato: servicio };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error.clase, "crear") };
    }
    throw error;
  }
}

function mensajeDeError(
  clase: ErrorApi["clase"],
  operacion: "cotizar" | "crear" | "disponibilidad" | "catalogos",
): string {
  if (clase === "sin-permisos" || clase === "sesion-expirada") {
    return "La API rechazó la operación. Verificá que el modo de demo local esté habilitado.";
  }
  if (clase === "sin-respuesta") {
    return "No pudimos conectar con el sistema. Revisá que el servidor esté funcionando.";
  }
  if (operacion === "catalogos") {
    return "No pudimos cargar clientes y tipos de vehículo. Cerrá y volvé a abrir el formulario.";
  }
  if (operacion === "cotizar") {
    return "No pudimos cotizar el viaje. Revisá los datos e intentá de nuevo.";
  }
  if (operacion === "disponibilidad") {
    return "No pudimos consultar la disponibilidad. Revisá la fecha y el tipo de vehículo.";
  }
  return "No pudimos registrar el servicio. Revisá los datos e intentá de nuevo.";
}
