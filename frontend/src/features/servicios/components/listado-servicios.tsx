import type { Servicio } from "@/features/servicios/types";

import { FilaServicio } from "./fila-servicio";

export function ListadoServicios({ servicios }: { servicios: Servicio[] }) {
  return (
    <table className="w-full border-collapse text-left max-sm:block">
      <caption className="sr-only">Servicios registrados</caption>
      <thead className="max-sm:hidden">
        <tr className="border-b border-linea">
          <th
            scope="col"
            className="py-2 pr-4 text-[0.8125rem] font-medium text-tinta-media"
          >
            Cliente y estado
          </th>
          <th
            scope="col"
            className="py-2 pr-4 text-[0.8125rem] font-medium text-tinta-media"
          >
            Vehículo
          </th>
          <th
            scope="col"
            className="py-2 pr-4 text-[0.8125rem] font-medium text-tinta-media"
          >
            Fecha
          </th>
          <th
            scope="col"
            className="py-2 text-right text-[0.8125rem] font-medium text-tinta-media"
          >
            Precio final
          </th>
        </tr>
      </thead>
      <tbody className="max-sm:block">
        {servicios.map((servicio) => (
          <FilaServicio key={servicio.id_servicio} servicio={servicio} />
        ))}
      </tbody>
    </table>
  );
}
