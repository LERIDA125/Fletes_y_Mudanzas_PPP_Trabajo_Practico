import type { Servicio } from "@/features/servicios/types";

import { FilaServicio } from "./fila-servicio";

export function ListadoServicios({ servicios }: { servicios: Servicio[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[980px] border-collapse text-left">
        <caption className="sr-only">Servicios registrados</caption>
        <thead>
          <tr className="h-11 border-b border-linea bg-papel/80 text-left text-xs font-semibold uppercase tracking-wider text-tinta-media">
            <th scope="col" className="px-4 py-3">
              ID
            </th>
            <th scope="col" className="px-4 py-3">
              Cliente
            </th>
            <th scope="col" className="px-4 py-3">
              Tipo de vehículo
            </th>
            <th scope="col" className="px-4 py-3">
              Fecha y hora
            </th>
            <th scope="col" className="px-4 py-3">
              Asignación
            </th>
            <th scope="col" className="px-4 py-3 text-right">
              Recorrido
            </th>
            <th scope="col" className="px-4 py-3 text-center">
              Estado
            </th>
            <th scope="col" className="px-4 py-3 text-right">
              Precio total
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-linea text-sm">
          {servicios.map((servicio) => (
            <FilaServicio key={servicio.id_servicio} servicio={servicio} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
