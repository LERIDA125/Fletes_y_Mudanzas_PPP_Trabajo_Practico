import { PanelCajaRendiciones } from "@/features/servicios/components/panel-caja-rendiciones";
import type { Servicio } from "@/features/servicios/types";
import { listarServicios } from "@/lib/api/servicios";

export const dynamic = "force-dynamic";

export default async function PaginaRendiciones() {
  let servicios: Servicio[] = [];

  try {
    const respuesta = await listarServicios(1, 100);
    servicios = respuesta.items;
  } catch (error) {
    // Si la API no está accesible en SSR, iniciamos con lista vacía
    console.error("No se pudieron cargar los servicios para rendiciones:", error);
  }

  return <PanelCajaRendiciones serviciosIniciales={servicios} />;
}
