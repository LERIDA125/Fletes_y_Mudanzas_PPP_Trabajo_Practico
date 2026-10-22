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
  const parametros = new URLSearchParams();

  if (criterio.q) {
    parametros.set("q", criterio.q);
  }
  parametros.set("page", String(criterio.page ?? 1));
  parametros.set("size", String(criterio.size ?? TAMANO_DE_PAGINA));

  return request<ListadoVehiculos>(`/api/vehiculos?${parametros.toString()}`);
}
