import type { Servicio } from "@/features/servicios/types";

const formatoMoneda = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
});

const formatoFecha = new Intl.DateTimeFormat("es-AR", {
  timeZone: "UTC",
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

function fechaLegible(fecha: string): string {
  const valor = new Date(`${fecha}T00:00:00Z`);
  return Number.isNaN(valor.getTime()) ? fecha : formatoFecha.format(valor);
}

function estadoLegible(estado: string): string {
  return estado.replaceAll("_", " ");
}

export function FilaServicio({ servicio }: { servicio: Servicio }) {
  return (
    <tr className="border-t border-linea align-top max-sm:block">
      <th
        scope="row"
        className="px-4 py-4 text-left text-[1rem] font-semibold text-tinta sm:px-0"
      >
        {servicio.razon_social_cliente}
        <span className="mt-1 block text-[0.875rem] font-normal text-tinta-media">
          Servicio #{servicio.id_servicio} · {estadoLegible(servicio.estado)}
        </span>
      </th>
      <td className="px-4 py-1 text-[0.875rem] text-tinta sm:px-0 sm:py-4">
        {servicio.descripcion_tipo_vehiculo}
        <span className="mt-1 block text-tinta-media">
          {servicio.patente_vehiculo ?? "Sin vehículo"}
          {servicio.nombre_chofer ? ` · ${servicio.nombre_chofer}` : " · Sin chofer"}
        </span>
      </td>
      <td className="px-4 py-1 text-[0.875rem] text-tinta sm:px-0 sm:py-4">
        {fechaLegible(servicio.fecha)}
        <span className="mt-1 block text-tinta-media">
          {servicio.hora_inicio ?? "Horario sin definir"}
        </span>
      </td>
      <td className="px-4 py-1 text-right text-[0.9375rem] font-semibold text-tinta tabular-nums sm:px-0 sm:py-4">
        <span className="text-[0.8125rem] font-normal text-tinta-media sm:hidden">
          Total:{" "}
        </span>
        {formatoMoneda.format(Number(servicio.precio_total))}
      </td>
    </tr>
  );
}
