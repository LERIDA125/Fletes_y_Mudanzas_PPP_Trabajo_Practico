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

function claseEstado(estado: string): string {
  switch (estado.toLocaleLowerCase("es-AR")) {
    case "pendiente":
      return "border-amber-200 bg-amber-50 text-amber-800";
    case "confirmado":
    case "en curso":
    case "en_curso":
      return "border-blue-200 bg-blue-50 text-blue-700";
    case "finalizado":
    case "cobrado":
      return "border-emerald-200 bg-emerald-50 text-emerald-800";
    default:
      return "border-linea bg-papel text-tinta-media";
  }
}

export function FilaServicio({ servicio }: { servicio: Servicio }) {
  return (
    <tr className="group align-middle transition-colors hover:bg-papel/60">
      <td className="whitespace-nowrap px-4 py-3.5 text-left font-mono text-xs font-semibold text-tinta-media tabular-nums">
        #{servicio.id_servicio}
      </td>
      <th scope="row" className="max-w-56 px-4 py-3.5 text-left font-normal">
        <span className="block truncate font-semibold text-tinta">
          {servicio.razon_social_cliente}
        </span>
        <span className="mt-0.5 block text-xs text-tinta-media">
          Cliente #{servicio.id_cliente}
        </span>
      </th>
      <td className="px-4 py-3.5">
        <span className="inline-flex rounded-md border border-linea bg-papel px-2.5 py-1 text-xs font-medium text-tinta">
          {servicio.descripcion_tipo_vehiculo}
        </span>
      </td>
      <td className="whitespace-nowrap px-4 py-3.5 text-tinta">
        <span className="block font-medium">{fechaLegible(servicio.fecha)}</span>
        <span className="mt-0.5 block text-xs text-tinta-media">
          {servicio.hora_inicio ?? "Horario sin definir"}
        </span>
      </td>
      <td className="max-w-52 px-4 py-3.5">
        <span className="block truncate font-medium text-tinta">
          {servicio.nombre_chofer ?? "Sin chofer"}
        </span>
        <span className="mt-0.5 block font-mono text-xs text-tinta-media">
          {servicio.patente_vehiculo ?? "Sin vehículo"}
        </span>
      </td>
      <td className="whitespace-nowrap px-4 py-3.5 text-right tabular-nums">
        <span className="block font-semibold text-tinta">
          {Number(servicio.distancia_total_km).toLocaleString("es-AR")} km
        </span>
        <span className="mt-0.5 block text-xs text-tinta-media">
          {Number(servicio.horas_estimadas).toLocaleString("es-AR")} h estimadas
        </span>
      </td>
      <td className="px-4 py-3.5 text-center">
        <span
          className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize ${claseEstado(
            servicio.estado,
          )}`}
        >
          <span
            className="size-1.5 rounded-full bg-current opacity-75"
            aria-hidden="true"
          />
          {estadoLegible(servicio.estado)}
        </span>
      </td>
      <td className="whitespace-nowrap px-4 py-3.5 text-right font-bold text-tinta tabular-nums">
        {formatoMoneda.format(Number(servicio.precio_total))}
      </td>
    </tr>
  );
}
