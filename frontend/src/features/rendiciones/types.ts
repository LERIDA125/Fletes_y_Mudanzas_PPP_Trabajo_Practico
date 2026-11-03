import type { components } from "@/types/openapi";

export type Rendicion = components["schemas"]["RendicionRead"];
export type ListadoRendiciones = components["schemas"]["RendicionListado"];
export type ResumenRendiciones = components["schemas"]["ResumenRendicionesRead"];
export type ServicioElegible = components["schemas"]["ServicioElegibleRead"];
export type NuevaRendicion = components["schemas"]["RendicionCreate"];
export type EstadoRendicion = components["schemas"]["RendicionEstadoUpdate"]["estado"];
