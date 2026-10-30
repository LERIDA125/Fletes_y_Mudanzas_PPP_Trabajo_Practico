"use server";

import { revalidatePath } from "next/cache";

import type { Chofer } from "@/features/choferes/types";
import type { ChoferValidado } from "@/features/choferes/schemas/chofer";
import {
  actualizarChofer,
  crearChofer,
  eliminarChofer as borrarChofer,
} from "@/lib/api/choferes";
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

export async function eliminarChofer(
  id: number,
): Promise<{ ok: true } | { ok: false; mensaje: string }> {
  try {
    await borrarChofer(id);
    revalidatePath("/choferes");
    revalidatePath("/servicios");
    revalidatePath("/agenda");
    revalidatePath("/");
    return { ok: true };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error, "eliminar") };
    }
    throw error;
  }
}

function mensajeDeError(
  error: ErrorApi,
  operacion: "guardar" | "eliminar" = "guardar",
): string {
  if (error.clase === "sin-permisos" || error.clase === "sesion-expirada") {
    return "Tu sesión venció o no tenés permisos. Volvé a iniciar sesión.";
  }
  if (error.clase === "sin-respuesta") {
    return "No pudimos conectar con el sistema. Revisá que el servidor esté funcionando.";
  }
  if (operacion === "eliminar") {
    if (error.status === 404) {
      return "El chofer ya no existe o fue dado de baja. Actualizá el listado.";
    }
    if (error.status === 409) {
      return "No se puede dar de baja un chofer con servicios o vehículos asociados.";
    }
    return "No pudimos dar de baja el chofer. Intentá de nuevo.";
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
