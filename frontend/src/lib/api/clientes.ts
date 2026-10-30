import type { Cliente, ListadoClientes } from "@/features/clientes/types";
import type { components } from "@/types/openapi";
import { requestAutenticado as request } from "./servidor";

export type CriterioDeBusqueda = {
  q?: string;
  page?: number;
  size?: number;
};

export type AltaCliente = components["schemas"]["ClienteCreate"];
export type EdicionCliente = components["schemas"]["ClienteUpdate"];

export type { Cliente, ListadoClientes };

export const TAMANO_DE_PAGINA = 20;

export async function listarClientes(
  criterio: CriterioDeBusqueda = {},
): Promise<ListadoClientes> {
  const parametros = new URLSearchParams();

  if (criterio.q) {
    parametros.set("q", criterio.q);
  }
  parametros.set("page", String(criterio.page ?? 1));
  parametros.set("size", String(criterio.size ?? TAMANO_DE_PAGINA));

  // Sin `use cache` y sin opciones de revalidación: el listado se resuelve en cada
  // request, que es el patrón de Cache Components para datos frescos detrás de Suspense.
  return request<ListadoClientes>(`/api/clientes?${parametros.toString()}`);
}

export async function crearCliente(datos: AltaCliente): Promise<Cliente> {
  return request<Cliente>("/api/clientes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

export async function actualizarCliente(
  id: number,
  datos: EdicionCliente,
): Promise<Cliente> {
  return request<Cliente>(`/api/clientes/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

export async function eliminarCliente(id: number): Promise<void> {
  return request<void>(`/api/clientes/${id}`, {
    method: "DELETE",
  });
}
