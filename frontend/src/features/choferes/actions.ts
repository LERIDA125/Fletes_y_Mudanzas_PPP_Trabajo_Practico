"use server";

import { revalidatePath } from "next/cache";

import type { Chofer } from "@/features/choferes/types";
import type { ChoferValidado } from "@/features/choferes/schemas/chofer";
import { actualizarChofer, crearChofer } from "@/lib/api/choferes";
import { ErrorApi } from "@/lib/api/http";

export type ResultadoChofer =
  | { ok: true; dato: Chofer }
  | { ok: false; mensaje: string; campo?: "nombre_completo" | "telefono" };

export async function guardarChofer(
  datos: ChoferValidado,
  id?: number,
): Promise<ResultadoChofer> {
  try {
    const chofer =
      id === undefined ? await crearChofer(datos) : await actualizarChofer(id, datos);
    revalidatePath("/choferes");
    revalidatePath("/servicios");
    revalidatePath("/agenda");
    revalidatePath("/");
    return { ok: true, dato: chofer };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error) };
    }
    throw error;
  }
}

function mensajeDeError(error: ErrorApi): string {
  if (error.clase === "sin-permisos" || error.clase === "sesion-expirada") {
    return "La API rechazó la operación. Verificá que el modo de demo local esté habilitado.";
  }
  if (error.clase === "sin-respuesta") {
    return "No pudimos conectar con el sistema. Revisá que el servidor esté funcionando.";
  }
  const detalle = error.detalle;
  if (detalle && typeof detalle === "object" && "detail" in detalle) {
    const mensaje = (detalle as { detail?: unknown }).detail;
    if (typeof mensaje === "string" && mensaje.trim()) {
      return mensaje;
    }
  }
  return "No pudimos guardar el chofer. Revisá los datos e intentá de nuevo.";
}
