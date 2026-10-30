import type { Servicio } from "@/features/servicios/types";

import { FilaServicio } from "./fila-servicio";

export function ListadoServicios({ servicios }: { servicios: Servicio[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left" aria-label="Servicios registrados">
        <caption className="sr-only">Servicios registrados</caption>
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50/70 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-slate-400">
            <th scope="col" className="py-3.5 pl-5 sm:pl-6">
              Horario
            </th>
            <th scope="col" className="px-4 py-3.5">
              Cliente
            </th>
            <th scope="col" className="px-4 py-3.5">
              Chofer asignado
            </th>
            <th scope="col" className="px-4 py-3.5">
              Vehículo
            </th>
            <th scope="col" className="px-4 py-3.5 text-right">
              Recorrido
            </th>
            <th scope="col" className="px-4 py-3.5 text-center">
              Estado
            </th>
            <th scope="col" className="px-4 py-3.5 text-right">
              Precio total
            </th>
            <th scope="col" className="py-3.5 pr-5 text-right sm:pr-6">
              <span className="sr-only">Acciones</span>
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 text-sm dark:divide-[#1e2c44]">
          {servicios.map((servicio) => (
            <FilaServicio key={servicio.id_servicio} servicio={servicio} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
