"use server";

import { revalidatePath } from "next/cache";

import type {
  AltaServicio,
  Cotizacion,
  Servicio,
  SolicitudCotizacion,
} from "@/features/servicios/types";
import { crearServicio, cotizarServicio } from "@/lib/api/servicios";
import { ErrorApi } from "@/lib/api/http";

export type ResultadoAccion<T> = { ok: true; dato: T } | { ok: false; mensaje: string };

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

export async function registrarServicio(
  solicitud: AltaServicio,
): Promise<ResultadoAccion<Servicio>> {
  try {
    const servicio = await crearServicio(solicitud);
    revalidatePath("/servicios");
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
  operacion: "cotizar" | "crear",
): string {
  if (clase === "sin-permisos" || clase === "sesion-expirada") {
    return "La API rechazó la operación. Verificá que el modo de demo local esté habilitado.";
  }
  if (clase === "sin-respuesta") {
    return "No pudimos conectar con el sistema. Revisá que el servidor esté funcionando.";
  }
  return operacion === "cotizar"
    ? "No pudimos cotizar el viaje. Revisá los datos e intentá de nuevo."
    : "No pudimos registrar el servicio. Revisá los datos e intentá de nuevo.";
}
