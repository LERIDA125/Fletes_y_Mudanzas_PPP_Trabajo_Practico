import type { components } from "@/types/openapi";

export type Servicio = components["schemas"]["ServicioRead"];
export type ListadoServicios = components["schemas"]["ServicioListado"];
export type Cotizacion = components["schemas"]["CotizacionRead"];
export type SolicitudCotizacion = components["schemas"]["CotizacionRequest"];
export type AltaServicio = components["schemas"]["ServicioCreate"];
export type ClienteOpcion = components["schemas"]["ClienteRead"];
export type TipoVehiculoOpcion = components["schemas"]["TipoVehiculoRead"];
