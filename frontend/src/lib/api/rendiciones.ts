import type {
  EstadoRendicion,
  ListadoRendiciones,
  NuevaRendicion,
  Rendicion,
  ServicioElegible,
} from "@/features/rendiciones/types";
import { requestAutenticado as request } from "./servidor";

export type CriterioDeRendiciones = {
  q?: string;
  page?: number;
  size?: number;
};

export const TAMANO_DE_PAGINA = 20;

export async function listarRendiciones(
  criterio: CriterioDeRendiciones = {},
): Promise<ListadoRendiciones> {
  const parametros = new URLSearchParams();

  if (criterio.q) {
    parametros.set("q", criterio.q);
  }
  parametros.set("page", String(criterio.page ?? 1));
  parametros.set("size", String(criterio.size ?? TAMANO_DE_PAGINA));

  return request<ListadoRendiciones>(`/api/rendiciones?${parametros.toString()}`);
}

export async function listarServiciosElegibles(): Promise<ServicioElegible[]> {
  return request<ServicioElegible[]>("/api/rendiciones/servicios-elegibles");
}

export async function crearRendicion(datos: NuevaRendicion): Promise<Rendicion> {
  return request<Rendicion>("/api/rendiciones", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

export async function cambiarEstadoRendicion(
  id: number,
  estado: EstadoRendicion,
): Promise<Rendicion> {
  return request<Rendicion>(`/api/rendiciones/${id}/estado`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado }),
  });
}
