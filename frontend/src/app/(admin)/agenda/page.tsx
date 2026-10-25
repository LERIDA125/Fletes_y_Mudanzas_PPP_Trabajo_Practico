import { AgendaCliente } from "./agenda-cliente";
import { listarServicios } from "@/lib/api/servicios";
import type { Servicio } from "@/features/servicios/types";
export const instant = false;

export default async function PaginaAgenda() {
  let servicios: Servicio[] = [];

  try {
    const res = await listarServicios(1, 100);
    servicios = res.items ?? [];
  } catch {
    servicios = [];
  }

  return <AgendaCliente serviciosIniciales={servicios} />;
}
