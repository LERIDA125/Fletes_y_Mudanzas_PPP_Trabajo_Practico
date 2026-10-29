import type {
  AltaServicio,
  ConsultaDisponibilidad,
  Cotizacion,
  Disponibilidad,
  ListadoServicios,
  EstadoServicio,
  Servicio,
  SolicitudCotizacion,
} from "@/features/servicios/types";
import type { components } from "@/types/openapi";
import { request } from "./http";

export const TAMANO_DE_PAGINA = 20;
export const POLLING_SERVICIOS_CHOFER_MS = 5000;
const TAMANO_DE_CATALOGOS = 100;

export async function listarServicios(
  pagina = 1,
  tamano = TAMANO_DE_PAGINA,
  idChofer?: number,
): Promise<ListadoServicios> {
  const parametros = new URLSearchParams({
    page: String(pagina),
    size: String(tamano),
  });
  if (idChofer !== undefined && idChofer > 0) {
    parametros.set("id_chofer", String(idChofer));
  }
  return request<ListadoServicios>(`/api/servicios?${parametros.toString()}`);
}

export function suscribirServiciosChofer(
  alRecibir: (listado: ListadoServicios) => void,
  alFallar?: (error: unknown) => void,
  intervaloMs = POLLING_SERVICIOS_CHOFER_MS,
  idChofer?: number,
): () => void {
  let activo = true;

  async function refrescar() {
    try {
      const datos = await listarServicios(1, 50, idChofer);
      if (activo) {
        alRecibir(datos);
      }
    } catch (error) {
      if (activo && alFallar) {
        alFallar(error);
      }
    }
  }

  void refrescar();
  const timer = setInterval(() => {
    void refrescar();
  }, intervaloMs);

  return () => {
    activo = false;
    clearInterval(timer);
  };
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

export async function consultarDisponibilidad(
  consulta: ConsultaDisponibilidad,
): Promise<Disponibilidad> {
  const parametros = new URLSearchParams({
    fecha: consulta.fecha,
    id_tipo_vehiculo: String(consulta.id_tipo_vehiculo),
    horas_estimadas: String(consulta.horas_estimadas),
  });
  if (consulta.hora_inicio) {
    parametros.set("hora_inicio", consulta.hora_inicio);
  }
  return request<Disponibilidad>(
    `/api/servicios/disponibilidad?${parametros.toString()}`,
  );
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

export async function cambiarEstadoServicio(
  idServicio: number,
  estado: EstadoServicio,
): Promise<Servicio> {
  return request<Servicio>(`/api/servicios/${idServicio}/estado`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado }),
  });
}

export async function eliminarServicio(idServicio: number): Promise<void> {
  return request<void>(`/api/servicios/${idServicio}`, {
    method: "DELETE",
  });
}

export async function cancelarServicio(
  idServicio: number,
  motivo: string,
): Promise<Servicio> {
  return request<Servicio>(`/api/servicios/${idServicio}/cancelar`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ motivo }),
  });
}
