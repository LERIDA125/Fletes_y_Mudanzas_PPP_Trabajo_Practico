"use server";

import type {
  Cotizacion,
  SolicitudCotizacion,
} from "@/features/cotizaciones/types";
import { calcularCotizacion as calcular } from "@/lib/api/cotizaciones";
import { ErrorApi } from "@/lib/api/http";

export type ResultadoCotizacion =
  | { ok: true; dato: Cotizacion }
  | { ok: false; mensaje: string };

export async function calcularCotizacion(
  solicitud: SolicitudCotizacion,
): Promise<ResultadoCotizacion> {
  try {
    return { ok: true, dato: await calcular(solicitud) };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error) };
    }
    throw error;
  }
}

function mensajeDeError(error: ErrorApi): string {
  if (error.clase === "sin-permisos" || error.clase === "sesion-expirada") {
    return "Tu sesión venció o no tenés permisos. Volvé a iniciar sesión.";
  }
  if (error.clase === "sin-respuesta") {
    return "No pudimos conectar con el sistema. Revisá que el servidor esté funcionando.";
  }
  const esErrorDeNegocio =
    error.status !== null && error.status >= 400 && error.status < 500;
  if (esErrorDeNegocio && error.message.trim()) {
    return error.message;
  }
  return "No pudimos calcular el precio sugerido. Revisá los datos e intentá de nuevo.";
}
