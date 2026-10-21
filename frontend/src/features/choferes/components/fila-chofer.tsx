import { fechaCorta, formatearSaldo } from "@/lib/utils/formato";

import type { Chofer } from "../types";

export function FilaChofer({ chofer }: { chofer: Chofer }) {
  return (
    <tr className="border-t border-linea align-top max-sm:block">
      <th
        scope="row"
        className="px-4 py-4 text-left text-[1rem] font-semibold text-tinta sm:px-0"
      >
        {chofer.nombre_completo}
        <span className="mt-1 block text-[0.875rem] font-normal text-tinta-media">
          {chofer.telefono}
        </span>
      </th>
      <td className="px-4 py-1 text-right text-[0.875rem] text-tinta tabular-nums sm:inline-block sm:px-0 sm:py-4">
        <span className="text-tinta-media sm:hidden">Saldo a favor: </span>
        {formatearSaldo(chofer.saldo_a_favor)}
      </td>
      <td className="px-4 py-1 text-right text-[0.875rem] text-tinta-media tabular-nums sm:inline-block sm:px-0 sm:py-4">
        <span className="text-tinta-media sm:hidden">Alta: </span>
        {fechaCorta(chofer.creado_en)}
      </td>
    </tr>
  );
}
