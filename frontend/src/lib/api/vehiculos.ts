import type { Vehiculo, ListadoVehiculos } from "@/features/vehiculos/types";
import { request } from "./http";

export type CriterioDeBusqueda = {
  q?: string;
  page?: number;
  size?: number;
};

export type { Vehiculo, ListadoVehiculos };

export const TAMANO_DE_PAGINA = 20;

export async function listarVehiculos(
  criterio: CriterioDeBusqueda = {},
): Promise<ListadoVehiculos> {
  const url = new URL("/api/vehiculos");

  if (criterio.q) {
    url.searchParams.set("q", criterio.q);
  }
  url.searchParams.set("page", String(criterio.page ?? 1));
  url.searchParams.set("size", String(criterio.size ?? TAMANO_DE_PAGINA));

  return request<ListadoVehiculos>(url.toString());
}
