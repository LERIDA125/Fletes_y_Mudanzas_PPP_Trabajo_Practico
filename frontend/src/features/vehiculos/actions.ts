"use server";

import { revalidatePath } from "next/cache";

import type { Chofer } from "@/features/choferes/types";
import type { TipoVehiculo, Vehiculo } from "@/features/vehiculos/types";
import type {
  TarifasTipoValidadas,
  VehiculoValidado,
} from "@/features/vehiculos/schemas/vehiculo";
import { listarChoferesActivos } from "@/lib/api/choferes";
import {
  actualizarTipoVehiculo,
  actualizarVehiculo,
  crearVehiculo,
  eliminarVehiculo as borrarVehiculo,
  listarTiposVehiculo,
} from "@/lib/api/vehiculos";
import { ErrorApi } from "@/lib/api/http";

export type ResultadoVehiculo =
  { ok: true; dato: Vehiculo } | { ok: false; mensaje: string };

export type ResultadoTarifas = { ok: true } | { ok: false; mensaje: string };

export type CatalogosVehiculo = {
  tiposVehiculo: TipoVehiculo[];
  choferes: Chofer[];
};

export type ResultadoCatalogosVehiculo =
  { ok: true; dato: CatalogosVehiculo } | { ok: false; mensaje: string };

/**
 * Catálogos para el alta/edición de vehículos. El diálogo los pide al abrirse,
 * así el encabezado y el botón "Nuevo vehículo" no dependen de la API.
 */
export async function obtenerCatalogosVehiculo(): Promise<ResultadoCatalogosVehiculo> {
  try {
    const [tiposVehiculo, choferes] = await Promise.all([
      listarTiposVehiculo(),
      listarChoferesActivos(),
    ]);
    return { ok: true, dato: { tiposVehiculo, choferes } };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error) };
    }
    throw error;
  }
}

export async function guardarVehiculo(
  datos: VehiculoValidado,
  id?: number,
): Promise<ResultadoVehiculo> {
  try {
    const vehiculo =
      id === undefined ? await crearVehiculo(datos) : await actualizarVehiculo(id, datos);
    revalidatePath("/vehiculos");
    revalidatePath("/servicios");
    revalidatePath("/agenda");
    revalidatePath("/");
    return { ok: true, dato: vehiculo };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error) };
    }
    throw error;
  }
}

export async function eliminarVehiculo(
  id: number,
): Promise<{ ok: true } | { ok: false; mensaje: string }> {
  try {
    await borrarVehiculo(id);
    revalidatePath("/vehiculos");
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

export async function guardarTarifasTipo(
  id: number,
  datos: TarifasTipoValidadas,
): Promise<ResultadoTarifas> {
  try {
    await actualizarTipoVehiculo(id, datos);
    revalidatePath("/vehiculos");
    revalidatePath("/servicios");
    revalidatePath("/cotizaciones");
    revalidatePath("/");
    return { ok: true };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error) };
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
    if (error.status === 409) {
      return "No se puede dar de baja un vehículo que tiene servicios registrados.";
    }
    if (error.status === 404) {
      return "El vehículo ya no existe o fue dado de baja. Actualizá el listado.";
    }
    return "No pudimos dar de baja el vehículo. Intentá de nuevo.";
  }
  const detalle = error.detalle;
  if (detalle && typeof detalle === "object" && "detail" in detalle) {
    const mensaje = (detalle as { detail?: unknown }).detail;
    if (typeof mensaje === "string" && mensaje.trim()) {
      return mensaje;
    }
  }
  return "No pudimos guardar los cambios. Revisá los datos e intentá de nuevo.";
}
