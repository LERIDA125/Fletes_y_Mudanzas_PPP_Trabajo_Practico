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
      return "border-panel-borde bg-panel-suave text-panel-secundario";
  }
}

export function FilaServicio({ servicio }: { servicio: Servicio }) {
  return (
    <tr className="group align-middle transition-colors hover:bg-panel-suave/70">
      <th
        scope="row"
        className="whitespace-nowrap px-3 py-3 text-left font-semibold text-panel-texto tabular-nums"
      >
        #{servicio.id_servicio}
      </th>
      <td className="max-w-56 px-3 py-3">
        <span className="block truncate font-medium text-panel-texto">
          {servicio.razon_social_cliente}
        </span>
        <span className="mt-0.5 block text-xs text-panel-secundario">
          Cliente #{servicio.id_cliente}
        </span>
      </td>
      <td className="px-3 py-3">
        <span className="inline-flex rounded border border-panel-borde bg-panel-suave px-2 py-1 text-xs font-medium text-panel-texto">
          {servicio.descripcion_tipo_vehiculo}
        </span>
      </td>
      <td className="whitespace-nowrap px-3 py-3 text-panel-texto">
        <span className="block">{fechaLegible(servicio.fecha)}</span>
        <span className="mt-0.5 block text-xs text-panel-secundario">
          {servicio.hora_inicio ?? "Horario sin definir"}
        </span>
      </td>
      <td className="max-w-52 px-3 py-3">
        <span className="block truncate text-panel-texto">
          {servicio.nombre_chofer ?? "Sin chofer"}
        </span>
        <span className="mt-0.5 block text-xs text-panel-secundario">
          {servicio.patente_vehiculo ?? "Sin vehículo"}
        </span>
      </td>
      <td className="whitespace-nowrap px-3 py-3 text-right tabular-nums">
        <span className="block font-medium text-panel-texto">
          {Number(servicio.distancia_total_km).toLocaleString("es-AR")} km
        </span>
        <span className="mt-0.5 block text-xs text-panel-secundario">
          {Number(servicio.horas_estimadas).toLocaleString("es-AR")} h estimadas
        </span>
      </td>
      <td className="px-3 py-3 text-center">
        <span
          className={`inline-flex whitespace-nowrap rounded border px-2.5 py-1 text-xs font-semibold capitalize ${claseEstado(
            servicio.estado,
          )}`}
        >
          {estadoLegible(servicio.estado)}
        </span>
      </td>
      <td className="whitespace-nowrap px-3 py-3 text-right font-semibold text-panel-texto tabular-nums">
        {formatoMoneda.format(Number(servicio.precio_total))}
      </td>
    </tr>
  );
}
