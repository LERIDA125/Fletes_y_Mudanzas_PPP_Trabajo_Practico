import type { Chofer, ListadoChoferes } from "@/features/choferes/types";
import { request } from "./http";

export type CriterioDeBusqueda = {
  q?: string;
  page?: number;
  size?: number;
};

export type { Chofer, ListadoChoferes };

export const TAMANO_DE_PAGINA = 20;

export async function listarChoferes(
  criterio: CriterioDeBusqueda = {},
): Promise<ListadoChoferes> {
  const parametros = new URLSearchParams();

  if (criterio.q) {
    parametros.set("q", criterio.q);
  }
  parametros.set("page", String(criterio.page ?? 1));
  parametros.set("size", String(criterio.size ?? TAMANO_DE_PAGINA));

  // Sin `use cache` y sin opciones de revalidación: el listado se resuelve en cada
  // request, que es el patrón de Cache Components para datos frescos detrás de Suspense.
  return request<ListadoChoferes>(`/api/choferes?${parametros.toString()}`);
}
