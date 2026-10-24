import type { Chofer } from "@/features/choferes/types";

import type { TipoVehiculo, Vehiculo } from "../types";
import { FilaVehiculo } from "./fila-vehiculo";

type Propiedades = {
  vehiculos: Vehiculo[];
  tiposVehiculo?: TipoVehiculo[];
  choferes?: Chofer[];
};

export function ListadoVehiculos({
  vehiculos,
  tiposVehiculo = [],
  choferes = [],
}: Propiedades) {
  return (
    <table className="w-full border-collapse text-left max-sm:block">
      <caption className="sr-only">Vehículos activos de la empresa</caption>
      <thead className="max-sm:hidden">
        <tr className="border-b border-linea">
          <th
            scope="col"
            className="py-2 pr-4 text-[0.8125rem] font-medium text-tinta-media"
          >
            Patente
          </th>
          <th
            scope="col"
            className="py-2 pr-4 text-[0.8125rem] font-medium text-tinta-media"
          >
            Tipo y capacidad
          </th>
          <th
            scope="col"
            className="py-2 pr-4 text-[0.8125rem] font-medium text-tinta-media"
          >
            Chofer habitual
          </th>
          <th
            scope="col"
            className="py-2 pr-4 text-right text-[0.8125rem] font-medium text-tinta-media"
          >
            Alta
          </th>
          <th
            scope="col"
            className="py-2 text-right text-[0.8125rem] font-medium text-tinta-media"
          >
            Acciones
          </th>
        </tr>
      </thead>
      <tbody className="max-sm:block">
        {vehiculos.map((vehiculo) => (
          <FilaVehiculo
            key={vehiculo.id}
            vehiculo={vehiculo}
            tiposVehiculo={tiposVehiculo}
            choferes={choferes}
          />
        ))}
      </tbody>
    </table>
  );
}
