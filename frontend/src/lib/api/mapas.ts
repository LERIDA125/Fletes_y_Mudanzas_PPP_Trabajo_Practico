import type { components } from "@/types/openapi";

import { requestAutenticado as request } from "./servidor";

type DireccionesRead = components["schemas"]["DireccionesRead"];
type DireccionBuscarRequest = components["schemas"]["DireccionBuscarRequest"];
type RutaRequest = components["schemas"]["RutaRequest"];
type RutaRead = components["schemas"]["RutaRead"];

export async function buscarDirecciones(
  consulta: DireccionBuscarRequest,
): Promise<DireccionesRead> {
  return request<DireccionesRead>("/api/mapas/direcciones", {
    method: "POST",
    body: JSON.stringify(consulta),
  });
}

export async function calcularRuta(solicitud: RutaRequest): Promise<RutaRead> {
  return request<RutaRead>("/api/mapas/ruta", {
    method: "POST",
    body: JSON.stringify(solicitud),
  });
}
