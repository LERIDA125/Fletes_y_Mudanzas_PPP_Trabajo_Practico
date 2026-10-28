import type { Cliente } from "../types";
import { FilaCliente } from "./fila-cliente";

export function ListadoClientes({ clientes }: { clientes: Cliente[] }) {
  return (
    <table className="w-full border-collapse text-left max-sm:block">
      <caption className="sr-only">Clientes dados de alta en el sistema</caption>
      <thead className="max-sm:hidden">
        <tr className="border-b border-linea">
          <th
            scope="col"
            className="py-2 pr-4 text-[0.8125rem] font-medium text-tinta-media"
          >
            Razón social
          </th>
          <th
            scope="col"
            className="py-2 pr-4 text-[0.8125rem] font-medium text-tinta-media"
          >
            Teléfono
          </th>
          <th
            scope="col"
            className="py-2 pr-4 text-[0.8125rem] font-medium text-tinta-media"
          >
            Cuenta corriente
          </th>
          <th
            scope="col"
            className="py-2 text-right text-[0.8125rem] font-medium text-tinta-media"
          >
            Alta
          </th>
          <th
            scope="col"
            className="w-px py-2 pl-4 text-right text-[0.8125rem] font-medium text-tinta-media"
          >
            <span className="sr-only">Acciones</span>
          </th>
        </tr>
      </thead>
      <tbody className="max-sm:block">
        {clientes.map((cliente) => (
          <FilaCliente key={cliente.id} cliente={cliente} />
        ))}
      </tbody>
    </table>
  );
}
