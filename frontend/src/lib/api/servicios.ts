import type {
  AltaServicio,
  Cotizacion,
  ListadoServicios,
  Servicio,
  SolicitudCotizacion,
} from "@/features/servicios/types";
import type { components } from "@/types/openapi";
import { request } from "./http";

export const TAMANO_DE_PAGINA = 20;
const TAMANO_DE_CATALOGOS = 100;

export async function listarServicios(
  pagina = 1,
  tamano = TAMANO_DE_PAGINA,
): Promise<ListadoServicios> {
  const parametros = new URLSearchParams({
    page: String(pagina),
    size: String(tamano),
  });
  return request<ListadoServicios>(`/api/servicios?${parametros.toString()}`);
}

export async function listarClientesParaAlta(): Promise<
  components["schemas"]["ClienteRead"][]
> {
  const parametros = new URLSearchParams({
    page: "1",
    size: String(TAMANO_DE_CATALOGOS),
  });
  const respuesta = await request<components["schemas"]["ClienteListado"]>(
    `/api/clientes?${parametros.toString()}`,
  );
  return respuesta.items;
}

export async function listarTiposParaAlta(): Promise<
  components["schemas"]["TipoVehiculoRead"][]
> {
  const parametros = new URLSearchParams({
    page: "1",
    size: String(TAMANO_DE_CATALOGOS),
  });
  const respuesta = await request<components["schemas"]["TipoVehiculoListado"]>(
    `/api/tipos-vehiculo?${parametros.toString()}`,
  );
  return respuesta.items;
}

export async function cotizarServicio(
  solicitud: SolicitudCotizacion,
): Promise<Cotizacion> {
  return request<Cotizacion>("/api/servicios/cotizar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(solicitud),
  });
}

export async function crearServicio(solicitud: AltaServicio): Promise<Servicio> {
  return request<Servicio>("/api/servicios", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(solicitud),
  });
}
