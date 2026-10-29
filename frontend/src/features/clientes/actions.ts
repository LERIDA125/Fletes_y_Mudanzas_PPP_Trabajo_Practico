"use server";

import { revalidatePath } from "next/cache";

import type { Cliente } from "@/features/clientes/types";
import type { ClienteValidado } from "@/features/clientes/schemas/cliente";
import {
  actualizarCliente as modificarCliente,
  crearCliente as altaCliente,
  eliminarCliente as borrarCliente,
} from "@/lib/api/clientes";
import { ErrorApi } from "@/lib/api/http";

export type ResultadoAccion<T> = { ok: true; dato: T } | { ok: false; mensaje: string };

export async function guardarCliente(
  datos: ClienteValidado,
  id?: number,
): Promise<ResultadoAccion<Cliente>> {
  try {
    const cliente =
      id === undefined ? await altaCliente(datos) : await modificarCliente(id, datos);
    revalidatePath("/clientes");
    revalidatePath("/servicios");
    revalidatePath("/agenda");
    revalidatePath("/");
    return { ok: true, dato: cliente };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error, "guardar") };
    }
    throw error;
  }
}

export async function eliminarCliente(id: number): Promise<ResultadoAccion<void>> {
  try {
    await borrarCliente(id);
    revalidatePath("/clientes");
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

function mensajeDeError(error: ErrorApi, operacion: "guardar" | "eliminar"): string {
  if (error.clase === "sin-permisos" || error.clase === "sesion-expirada") {
    return "La API rechazó la operación. Verificá que el modo de demo local esté habilitado.";
  }
  if (error.clase === "sin-respuesta") {
    return "No pudimos conectar con el sistema. Revisá que el servidor esté funcionando.";
  }
  if (operacion === "eliminar") {
    if (error.status === 409) {
      return "No se puede dar de baja un cliente que tiene servicios registrados.";
    }
    if (error.status === 404) {
      return "El cliente ya no existe o fue dado de baja. Actualizá el listado.";
    }
    return "No pudimos dar de baja el cliente. Intentá de nuevo.";
  }
  // Para 409 (razón social duplicada) el backend devuelve un detalle en español
  // que conviene mostrar tal cual. Los 422 ya se validan en el formulario, pero
  // si igual llegan se muestra el detalle de FastAPI.
  if (error.status === 409 || error.status === 422) {
    return (
      error.message ||
      "No pudimos guardar los cambios. Revisá los datos e intentá de nuevo."
    );
  }
  return "No pudimos guardar los cambios. Revisá los datos e intentá de nuevo.";
}
