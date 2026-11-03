"use server";

import { revalidatePath } from "next/cache";

import { ErrorApi } from "@/lib/api/http";
import {
  cambiarEstadoRendicion as cambiarEstadoApi,
  crearRendicion as altaRendicion,
} from "@/lib/api/rendiciones";
import type {
  EstadoRendicion,
  NuevaRendicion,
  Rendicion,
} from "@/features/rendiciones/types";

export type ResultadoAccion<T> = { ok: true; dato: T } | { ok: false; mensaje: string };

export async function guardarRendicion(
  datos: NuevaRendicion,
): Promise<ResultadoAccion<Rendicion>> {
  try {
    const rendicion = await altaRendicion(datos);
    revalidatePath("/rendiciones");
    revalidatePath("/");
    return { ok: true, dato: rendicion };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error, "guardar") };
    }
    throw error;
  }
}

export async function cambiarEstado(
  id: number,
  estado: EstadoRendicion,
): Promise<ResultadoAccion<Rendicion>> {
  try {
    const rendicion = await cambiarEstadoApi(id, estado);
    revalidatePath("/rendiciones");
    revalidatePath("/");
    return { ok: true, dato: rendicion };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error, "estado") };
    }
    throw error;
  }
}

function mensajeDeError(error: ErrorApi, operacion: "guardar" | "estado"): string {
  if (error.clase === "sin-permisos" || error.clase === "sesion-expirada") {
    return "Tu sesión venció o no tenés permisos. Volvé a iniciar sesión.";
  }
  if (error.clase === "sin-respuesta") {
    return "No pudimos conectar con el sistema. Revisá que el servidor esté funcionando.";
  }
  if (error.status === 404) {
    return "La rendición o el servicio ya no existe. Actualizá el listado.";
  }
  if (error.status === 409) {
    return (
      error.message ||
      "El servicio ya tiene una rendición registrada o no está finalizado."
    );
  }
  if (error.status === 422) {
    return (
      error.message ||
      (operacion === "guardar"
        ? "Revisá los importes y el servicio seleccionado."
        : "El estado elegido no es válido.")
    );
  }
  return operacion === "guardar"
    ? "No pudimos registrar la rendición. Intentá de nuevo."
    : "No pudimos actualizar el estado. Intentá de nuevo.";
}
