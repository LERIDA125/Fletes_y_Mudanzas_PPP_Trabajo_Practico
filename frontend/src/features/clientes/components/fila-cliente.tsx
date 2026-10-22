import { fechaCorta } from "@/lib/utils/formato";

import type { Cliente } from "../types";

export function FilaCliente({ cliente }: { cliente: Cliente }) {
  return (
    <tr className="border-t border-linea align-top max-sm:block">
      <th
        scope="row"
        className="px-4 py-4 text-left text-[1rem] font-semibold text-tinta sm:px-0"
      >
        {cliente.razon_social}
        <span className="mt-1 block text-[0.875rem] font-normal text-tinta-media">
          {cliente.direccion_habitual}
        </span>
      </th>
      <td className="px-4 py-1 text-[0.875rem] text-tinta tabular-nums sm:inline-block sm:px-0 sm:py-4">
        <span className="text-tinta-media sm:hidden">Teléfono: </span>
        {cliente.telefono}
      </td>
      <td className="px-4 py-1 text-[0.875rem] text-tinta sm:inline-block sm:px-0 sm:py-4">
        <span className="text-tinta-media sm:hidden">Cuenta corriente: </span>
        {cliente.tiene_cuenta_corriente ? "Sí" : "No"}
      </td>
      <td className="px-4 py-1 text-right text-[0.875rem] text-tinta-media tabular-nums sm:inline-block sm:px-0 sm:py-4">
        <span className="text-tinta-media sm:hidden">Alta: </span>
        {fechaCorta(cliente.creado_en)}
      </td>
    </tr>
  );
}
