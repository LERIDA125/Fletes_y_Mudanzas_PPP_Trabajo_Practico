import { CarFront, MoreHorizontal } from "lucide-react";

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

function iniciales(nombre: string): string {
  return nombre
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join("");
}

const statusStyles: Record<string, string> = {
  "en curso": "border-sky-200 bg-sky-50 text-sky-700",
  en_curso: "border-sky-200 bg-sky-50 text-sky-700",
  pendiente: "border-amber-200 bg-amber-50 text-amber-700",
  finalizado: "border-emerald-200 bg-emerald-50 text-emerald-700",
  confirmado: "border-blue-200 bg-blue-50 text-blue-700",
  cobrado: "border-purple-200 bg-purple-50 text-purple-700",
};

export function FilaServicio({ servicio }: { servicio: Servicio }) {
  const estadoClave = servicio.estado.toLowerCase();
  const claseBadge =
    statusStyles[estadoClave] ?? "border-slate-200 bg-slate-50 text-slate-700";

  return (
    <tr className="transition-colors hover:bg-slate-50/70">
      <td className="whitespace-nowrap py-3.5 pl-5 sm:pl-6">
        <span className="block font-semibold text-slate-900">
          {servicio.hora_inicio ?? "—"}
        </span>
        <span className="block text-xs text-slate-500">
          {fechaLegible(servicio.fecha)}
        </span>
      </td>

      <th
        scope="row"
        className="max-w-56 px-4 py-3.5 text-left font-normal whitespace-nowrap"
      >
        <span className="block truncate font-semibold text-slate-900">
          {servicio.razon_social_cliente}
        </span>
        <span className="mt-0.5 block text-xs text-slate-500">
          Cliente #{servicio.id_cliente}
        </span>
      </th>

      <td className="px-4 py-3.5 whitespace-nowrap">
        <div className="flex items-center gap-2">
          {servicio.nombre_chofer ? (
            <>
              <div className="flex size-7 items-center justify-center rounded-full bg-slate-100 text-[10px] font-semibold text-slate-600">
                {iniciales(servicio.nombre_chofer)}
              </div>
              <span className="font-medium text-slate-900">{servicio.nombre_chofer}</span>
            </>
          ) : (
            <>
              <div className="flex size-7 items-center justify-center rounded-full border border-dashed border-slate-300 text-xs text-slate-400">
                —
              </div>
              <span className="text-slate-400">Sin chofer</span>
            </>
          )}
        </div>
      </td>

      <td className="px-4 py-3.5 whitespace-nowrap">
        <span className="inline-flex items-center gap-1.5 text-slate-700">
          <CarFront className="size-4 text-slate-400" />
          <span>{servicio.descripcion_tipo_vehiculo}</span>
          {servicio.patente_vehiculo ? (
            <span className="font-mono text-xs text-slate-500">
              ({servicio.patente_vehiculo})
            </span>
          ) : (
            <span className="text-xs text-slate-400">· Sin vehículo</span>
          )}
        </span>
      </td>

      <td className="whitespace-nowrap px-4 py-3.5 text-right tabular-nums">
        <span className="block font-medium text-slate-800">
          {Number(servicio.distancia_total_km).toLocaleString("es-AR")} km
        </span>
        <span className="mt-0.5 block text-xs text-slate-400">
          {Number(servicio.horas_estimadas).toLocaleString("es-AR")} h estimadas
        </span>
      </td>

      <td className="px-4 py-3.5 text-center whitespace-nowrap">
        <span
          className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize ${claseBadge}`}
        >
          {servicio.estado.replaceAll("_", " ")}
        </span>
      </td>

      <td className="whitespace-nowrap px-4 py-3.5 text-right font-bold text-slate-900 tabular-nums">
        {formatoMoneda.format(Number(servicio.precio_total))}
      </td>

      <td className="whitespace-nowrap py-3.5 pr-5 text-right sm:pr-6">
        <button
          type="button"
          aria-label={`Opciones de ${servicio.razon_social_cliente}`}
          className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
        >
          <MoreHorizontal className="size-4" />
        </button>
      </td>
    </tr>
  );
}
