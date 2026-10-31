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
  SolicitudFinalizarViaje,
  TipoVehiculoOpcion,
} from "@/features/servicios/types";
import {
  aprobarRendicionServicio as aprobarRendicionEnApi,
  cancelarServicio as anularServicio,
  consultarDisponibilidad,
  crearServicio,
  cambiarEstadoServicio as actualizarEstadoServicio,
  cotizarServicio,
  eliminarServicio as borrarServicio,
  finalizarViajeServicio as finalizarViajeEnApi,
  listarServiciosAsignados,
  listarClientesParaAlta,
  listarTiposParaAlta,
  observarRendicionServicio as observarRendicionEnApi,
} from "@/lib/api/servicios";
import { ErrorApi } from "@/lib/api/http";
import { exigirRol } from "@/lib/auth/guards";

export type ResultadoAccion<T> = { ok: true; dato: T } | { ok: false; mensaje: string };

export type CatalogosServicio = {
  clientes: ClienteOpcion[];
  tiposVehiculo: TipoVehiculoOpcion[];
};

export async function obtenerServiciosChofer(): Promise<ResultadoAccion<Servicio[]>> {
  await exigirRol("CHOFER");

  try {
    return { ok: true, dato: await listarServiciosAsignados() };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error, "listar-chofer") };
    }
    throw error;
  }
}

export async function iniciarViajeChofer(
  idServicio: number,
): Promise<ResultadoAccion<Servicio>> {
  await exigirRol("CHOFER");

  try {
    const servicio = await actualizarEstadoServicio(idServicio, "en curso");
    revalidatePath("/chofer");
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

export async function finalizarViajeChofer(
  idServicio: number,
  solicitud: SolicitudFinalizarViaje,
): Promise<ResultadoAccion<Servicio>> {
  await exigirRol("CHOFER");

  try {
    const servicio = await finalizarViajeEnApi(idServicio, solicitud);
    revalidatePath("/chofer");
    revalidatePath("/rendiciones");
    revalidatePath("/servicios");
    revalidatePath("/agenda");
    revalidatePath("/");
    return { ok: true, dato: servicio };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error, "finalizar") };
    }
    throw error;
  }
}

export async function aprobarRendicionServicio(
  idServicio: number,
): Promise<ResultadoAccion<Servicio>> {
  await exigirRol("ADMIN");

  try {
    const servicio = await aprobarRendicionEnApi(idServicio);
    revalidatePath("/rendiciones");
    revalidatePath("/servicios");
    revalidatePath("/agenda");
    revalidatePath("/");
    return { ok: true, dato: servicio };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error, "rendicion") };
    }
    throw error;
  }
}

export async function observarRendicionServicio(
  idServicio: number,
  observacion: string,
): Promise<ResultadoAccion<Servicio>> {
  await exigirRol("ADMIN");

  try {
    const servicio = await observarRendicionEnApi(idServicio, observacion);
    revalidatePath("/rendiciones");
    revalidatePath("/servicios");
    return { ok: true, dato: servicio };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error, "rendicion") };
    }
    throw error;
  }
}

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
    | "finalizar"
    | "rendicion"
    | "cancelar"
    | "eliminar"
    | "listar-chofer",
): string {
  if (error.clase === "sin-permisos" || error.clase === "sesion-expirada") {
    return "Tu sesión venció o no tenés permisos. Volvé a iniciar sesión.";
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
  if (operacion === "finalizar") {
    return "No pudimos finalizar el viaje. Verificá la foto del remito y el monto cobrado.";
  }
  if (operacion === "rendicion") {
    return "No pudimos actualizar la rendición del servicio. Intentá de nuevo.";
  }
  if (operacion === "cancelar") {
    return "No pudimos cancelar el servicio. Revisá el estado actual e intentá de nuevo.";
  }
  if (operacion === "eliminar") {
    return "No pudimos eliminar el servicio. Intentá de nuevo.";
  }
  if (operacion === "listar-chofer") {
    return "No pudimos actualizar tus viajes. Revisá la conexión e intentá de nuevo.";
  }
  return "No pudimos registrar el servicio. Revisá los datos e intentá de nuevo.";
}
