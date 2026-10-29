import type { components } from "@/types/openapi";

export type Servicio = components["schemas"]["ServicioRead"];
export type ListadoServicios = components["schemas"]["ServicioListado"];
export type Cotizacion = components["schemas"]["CotizacionRead"];
export type SolicitudCotizacion = components["schemas"]["CotizacionRequest"];
export type AltaServicio = components["schemas"]["ServicioCreate"];
export type NuevoClienteServicio = components["schemas"]["ClienteCreate"];
export type ClienteOpcion = components["schemas"]["ClienteRead"];
export type TipoVehiculoOpcion = components["schemas"]["TipoVehiculoRead"];
export type Disponibilidad = components["schemas"]["DisponibilidadRead"];
export type ChoferDisponible = components["schemas"]["ChoferRead"];
export type VehiculoDisponible = components["schemas"]["VehiculoListadoRead"];

export type EstadoServicio =
  | "pendiente"
  | "confirmado"
  | "en curso"
  | "finalizado"
  | "cobrado"
  | "cancelado";

export type ConsultaDisponibilidad = {
  fecha: string;
  id_tipo_vehiculo: number;
  horas_estimadas: number;
  hora_inicio: string | null;
};
