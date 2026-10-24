import type { Vehiculo, ListadoVehiculos } from "@/features/vehiculos/types";
import type { components } from "@/types/openapi";
import { request } from "./http";

export type CriterioDeBusqueda = {
  q?: string;
  page?: number;
  size?: number;
};

export type AltaVehiculo = components["schemas"]["VehiculoCreate"];
export type EdicionVehiculo = components["schemas"]["VehiculoUpdate"];
export type TipoVehiculo = components["schemas"]["TipoVehiculoRead"];
export type ListadoTiposVehiculo = components["schemas"]["TipoVehiculoListado"];
export type EdicionTipoVehiculo = components["schemas"]["TipoVehiculoUpdate"];

export type { Vehiculo, ListadoVehiculos };

export const TAMANO_DE_PAGINA = 20;
const TAMANO_DE_CATALOGO = 100;

export async function listarVehiculos(
  criterio: CriterioDeBusqueda = {},
): Promise<ListadoVehiculos> {
  const parametros = new URLSearchParams();

  if (criterio.q) {
    parametros.set("q", criterio.q);
  }
  parametros.set("page", String(criterio.page ?? 1));
  parametros.set("size", String(criterio.size ?? TAMANO_DE_PAGINA));

  return request<ListadoVehiculos>(`/api/vehiculos?${parametros.toString()}`);
}

export async function crearVehiculo(datos: AltaVehiculo): Promise<Vehiculo> {
  return request<Vehiculo>("/api/vehiculos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

export async function actualizarVehiculo(
  id: number,
  datos: EdicionVehiculo,
): Promise<Vehiculo> {
  return request<Vehiculo>(`/api/vehiculos/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

export async function listarTiposVehiculo(): Promise<TipoVehiculo[]> {
  const parametros = new URLSearchParams({
    page: "1",
    size: String(TAMANO_DE_CATALOGO),
  });
  const respuesta = await request<ListadoTiposVehiculo>(
    `/api/tipos-vehiculo?${parametros.toString()}`,
  );
  return respuesta.items;
}

export async function actualizarTipoVehiculo(
  id: number,
  datos: EdicionTipoVehiculo,
): Promise<TipoVehiculo> {
  return request<TipoVehiculo>(`/api/tipos-vehiculo/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}
