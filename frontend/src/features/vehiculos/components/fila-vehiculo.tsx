import { fechaCorta } from "@/lib/utils/formato";

import type { Vehiculo } from "../types";

const formatoCapacidad = new Intl.NumberFormat("es-AR", {
  maximumFractionDigits: 2,
});

export function FilaVehiculo({ vehiculo }: { vehiculo: Vehiculo }) {
  return (
    <tr className="border-t border-linea align-top max-sm:block">
      <th
        scope="row"
        className="break-words px-4 py-4 text-left text-[1rem] font-semibold text-tinta sm:px-0"
      >
        {vehiculo.patente}
      </th>
      <td className="break-words px-4 py-1 text-[0.875rem] text-tinta sm:px-0 sm:py-4">
        <span className="text-tinta-media sm:hidden">Tipo y capacidad: </span>
        <span>{vehiculo.descripcion_tipo_vehiculo}</span>
        <span className="block text-tinta-media">
          {formatoCapacidad.format(vehiculo.capacidad_carga_kg)} kg
        </span>
      </td>
      <td className="break-words px-4 py-1 text-[0.875rem] text-tinta sm:px-0 sm:py-4">
        <span className="text-tinta-media sm:hidden">Chofer habitual: </span>
        {vehiculo.nombre_chofer_habitual ?? "Sin chofer habitual"}
      </td>
      <td className="px-4 py-1 text-right text-[0.875rem] text-tinta-media tabular-nums sm:px-0 sm:py-4">
        <span className="text-tinta-media sm:hidden">Alta: </span>
        {fechaCorta(vehiculo.creado_en)}
      </td>
    </tr>
  );
}
