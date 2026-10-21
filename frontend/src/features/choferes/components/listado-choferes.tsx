import type { Chofer } from "../types";
import { FilaChofer } from "./fila-chofer";

export function ListadoChoferes({ choferes }: { choferes: Chofer[] }) {
  return (
    <table className="w-full border-collapse text-left max-sm:block">
      <caption className="sr-only">Choferes activos de la empresa</caption>
      <thead className="max-sm:hidden">
        <tr className="border-b border-linea">
          <th
            scope="col"
            className="py-2 pr-4 text-[0.8125rem] font-medium text-tinta-media"
          >
            Nombre completo
          </th>
          <th
            scope="col"
            className="py-2 pr-4 text-right text-[0.8125rem] font-medium text-tinta-media"
          >
            Saldo a favor
          </th>
          <th
            scope="col"
            className="py-2 text-right text-[0.8125rem] font-medium text-tinta-media"
          >
            Alta
          </th>
        </tr>
      </thead>
      <tbody className="max-sm:block">
        {choferes.map((chofer) => (
          <FilaChofer key={chofer.id} chofer={chofer} />
        ))}
      </tbody>
    </table>
  );
}
