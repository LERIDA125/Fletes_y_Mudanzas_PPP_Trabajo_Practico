import type {
  Cotizacion,
  SolicitudCotizacion,
} from "@/features/cotizaciones/types";
import { requestAutenticado as request } from "./servidor";

export async function calcularCotizacion(
  solicitud: SolicitudCotizacion,
): Promise<Cotizacion> {
  return request<Cotizacion>("/api/cotizaciones/calcular", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(solicitud),
  });
}
