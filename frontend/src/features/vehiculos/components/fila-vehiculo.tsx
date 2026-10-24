import type { Chofer } from "@/features/choferes/types";
import { fechaCorta } from "@/lib/utils/formato";

import type { TipoVehiculo, Vehiculo } from "../types";
import { DialogoVehiculo } from "./dialogo-vehiculo";

const formatoCapacidad = new Intl.NumberFormat("es-AR", {
  maximumFractionDigits: 2,
});

type Propiedades = {
  vehiculo: Vehiculo;
  tiposVehiculo?: TipoVehiculo[];
  choferes?: Chofer[];
};

export function FilaVehiculo({
  vehiculo,
  tiposVehiculo = [],
  choferes = [],
}: Propiedades) {
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
      <td className="px-4 py-1 text-right sm:px-0 sm:py-3">
        <DialogoVehiculo
          vehiculo={vehiculo}
          tiposVehiculo={tiposVehiculo}
          choferes={choferes}
        />
      </td>
    </tr>
  );
}
