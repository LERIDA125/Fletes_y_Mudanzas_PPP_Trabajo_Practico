"use server";

import { revalidatePath } from "next/cache";

import type {
  AltaServicio,
  ClienteOpcion,
  ConsultaDisponibilidad,
  Cotizacion,
  Disponibilidad,
  EstadoServicio,
  Servicio,
  SolicitudCotizacion,
  TipoVehiculoOpcion,
} from "@/features/servicios/types";
import {
  cancelarServicio as anularServicio,
  consultarDisponibilidad,
  crearServicio,
  cambiarEstadoServicio as actualizarEstadoServicio,
  cotizarServicio,
  eliminarServicio as borrarServicio,
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
      return { ok: false, mensaje: mensajeDeError(error, "catalogos") };
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
      return { ok: false, mensaje: mensajeDeError(error, "cotizar") };
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
      return { ok: false, mensaje: mensajeDeError(error, "disponibilidad") };
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
      return { ok: false, mensaje: mensajeDeError(error, "crear") };
    }
    throw error;
  }
}

export async function cambiarEstadoServicio(
  idServicio: number,
  estado: EstadoServicio,
): Promise<ResultadoAccion<Servicio>> {
  try {
    const servicio = await actualizarEstadoServicio(idServicio, estado);
    revalidatePath("/servicios");
    revalidatePath("/agenda");
    revalidatePath("/");
    return { ok: true, dato: servicio };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error, "cambiar-estado") };
    }
    throw error;
  }
}

export async function cancelarServicio(
  idServicio: number,
  motivo: string,
): Promise<ResultadoAccion<Servicio>> {
  try {
    const servicio = await anularServicio(idServicio, motivo);
    revalidatePath("/servicios");
    revalidatePath("/agenda");
    revalidatePath("/");
    return { ok: true, dato: servicio };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error, "cancelar") };
    }
    throw error;
  }
}

export async function eliminarServicio(
  idServicio: number,
): Promise<ResultadoAccion<void>> {
  try {
    await borrarServicio(idServicio);
    revalidatePath("/servicios");
    revalidatePath("/agenda");
    revalidatePath("/");
    return { ok: true, dato: undefined };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error, "eliminar") };
    }
    throw error;
  }
}

function mensajeDeError(
  error: ErrorApi,
  operacion:
    | "cotizar"
    | "crear"
    | "disponibilidad"
    | "catalogos"
    | "cambiar-estado"
    | "cancelar"
    | "eliminar",
): string {
  if (error.clase === "sin-permisos" || error.clase === "sesion-expirada") {
    return "La API rechazó la operación. Verificá que el modo de demo local esté habilitado.";
  }
  if (error.clase === "sin-respuesta") {
    return "No pudimos conectar con el sistema. Revisá que el servidor esté funcionando.";
  }
  // La API rechazó la operación por una regla de negocio (422/409/404): mostrar
  // su detalle tal cual en vez de taparlo con un texto genérico.
  const esErrorDeNegocio =
    error.status !== null && error.status >= 400 && error.status < 500;
  if (esErrorDeNegocio && error.message.trim()) {
    return error.message;
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
  if (operacion === "cambiar-estado") {
    return "No pudimos cambiar el estado del servicio. Revisá el estado actual e intentá de nuevo.";
  }
  if (operacion === "cancelar") {
    return "No pudimos cancelar el servicio. Revisá el estado actual e intentá de nuevo.";
  }
  if (operacion === "eliminar") {
    return "No pudimos eliminar el servicio. Intentá de nuevo.";
  }
  return "No pudimos registrar el servicio. Revisá los datos e intentá de nuevo.";
}
