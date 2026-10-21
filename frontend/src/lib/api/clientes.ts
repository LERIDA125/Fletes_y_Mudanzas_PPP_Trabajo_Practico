import type { Cliente, ListadoClientes } from "@/features/clientes/types";
import { request } from "./http";

export type CriterioDeBusqueda = {
  q?: string;
  page?: number;
  size?: number;
};

export type { Cliente, ListadoClientes };

export const TAMANO_DE_PAGINA = 20;

export async function listarClientes(
  criterio: CriterioDeBusqueda = {},
): Promise<ListadoClientes> {
  const url = new URL("/api/clientes");

  if (criterio.q) {
    url.searchParams.set("q", criterio.q);
  }
  url.searchParams.set("page", String(criterio.page ?? 1));
  url.searchParams.set("size", String(criterio.size ?? TAMANO_DE_PAGINA));

  // Sin `use cache` y sin opciones de revalidación: el listado se resuelve en cada
  // request, que es el patrón de Cache Components para datos frescos detrás de Suspense.
  return request<ListadoClientes>(url.toString());
}
