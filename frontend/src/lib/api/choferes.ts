import type { Chofer, ListadoChoferes } from "@/features/choferes/types";
import type { components } from "@/types/openapi";
import { requestAutenticado as request } from "./servidor";

export type CriterioDeBusqueda = {
  q?: string;
  page?: number;
  size?: number;
};

export type AltaChofer = components["schemas"]["ChoferCreate"];
export type EdicionChofer = components["schemas"]["ChoferUpdate"];

export type { Chofer, ListadoChoferes };

export const TAMANO_DE_PAGINA = 20;
const TAMANO_DE_CATALOGO = 100;

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

export async function listarChoferesActivos(): Promise<Chofer[]> {
  const parametros = new URLSearchParams({
    page: "1",
    size: String(TAMANO_DE_CATALOGO),
  });
  const respuesta = await request<ListadoChoferes>(
    `/api/choferes?${parametros.toString()}`,
  );
  return respuesta.items;
}

export async function crearChofer(datos: AltaChofer): Promise<Chofer> {
  return request<Chofer>("/api/choferes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

export async function actualizarChofer(
  id: number,
  datos: EdicionChofer,
): Promise<Chofer> {
  return request<Chofer>(`/api/choferes/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

export async function eliminarChofer(id: number): Promise<void> {
  return request<void>(`/api/choferes/${id}`, {
    method: "DELETE",
  });
}
