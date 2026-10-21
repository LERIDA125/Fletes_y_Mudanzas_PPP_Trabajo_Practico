import type { Servicio } from "@/features/servicios/types";

import { FilaServicio } from "./fila-servicio";

export function ListadoServicios({ servicios }: { servicios: Servicio[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[980px] border-collapse text-left">
      <caption className="sr-only">Servicios registrados</caption>
        <thead>
          <tr className="h-10 border-b-2 border-panel-borde bg-panel-suave text-left text-[0.6875rem] font-semibold tracking-wide text-panel-secundario">
            <th scope="col" className="px-3 py-2">ID</th>
            <th scope="col" className="px-3 py-2">Cliente</th>
            <th scope="col" className="px-3 py-2">Tipo de vehículo</th>
            <th scope="col" className="px-3 py-2">Fecha y hora</th>
            <th scope="col" className="px-3 py-2">Asignación</th>
            <th scope="col" className="px-3 py-2 text-right">Recorrido</th>
            <th scope="col" className="px-3 py-2 text-center">Estado</th>
            <th scope="col" className="px-3 py-2 text-right">Precio total</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-panel-borde text-[0.8125rem]">
          {servicios.map((servicio) => (
            <FilaServicio key={servicio.id_servicio} servicio={servicio} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
