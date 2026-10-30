import { Clock3, MapPin, Truck, UserRound } from "lucide-react";

import type { Servicio } from "@/features/servicios/types";
import { formatearSaldo } from "@/lib/utils/formato";

const ESTADOS: Record<string, { etiqueta: string; clase: string }> = {
  pendiente: {
    etiqueta: "Pendiente",
    clase: "bg-[#e2f2ec] text-[#28745f]",
  },
  confirmado: {
    etiqueta: "Confirmado",
    clase: "bg-[#e2f2ec] text-[#28745f]",
  },
  "en curso": {
    etiqueta: "En camino",
    clase: "bg-[#fff0d9] text-[#a76312]",
  },
  finalizado: {
    etiqueta: "Finalizado",
    clase: "bg-[#e8edf1] text-[#58676d]",
  },
  cobrado: {
    etiqueta: "Cobrado",
    clase: "bg-[#e8edf1] text-[#58676d]",
  },
  cancelado: {
    etiqueta: "Cancelado",
    clase: "bg-[#fde9e7] text-[#a73b32]",
  },
};

function horaConPeriodo(hora: string | null): { hora: string; periodo: string } {
  if (!hora) {
    return { hora: "Horario", periodo: "a confirmar" };
  }

  const [horasTexto, minutos = "00"] = hora.split(":");
  const horas = Number(horasTexto);
  const periodo = horas < 12 ? "AM" : "PM";

  return {
    hora: `${String(horas % 12 || 12).padStart(2, "0")}:${minutos}`,
    periodo,
  };
}

export function TarjetaViajeChofer({
  servicio,
  numero,
}: {
  servicio: Servicio;
  numero: number;
}) {
  const horario = horaConPeriodo(servicio.hora_inicio);
  const estado = ESTADOS[servicio.estado] ?? ESTADOS.pendiente;

  return (
    <article
      aria-labelledby={`viaje-${servicio.id_servicio}`}
      className="overflow-hidden rounded-[1.2rem] border border-[#dce9e4] bg-white shadow-[0_8px_24px_-20px_rgba(27,65,57,0.5)]"
    >
      <header className="flex items-center justify-between gap-2 border-b border-[#edf1ef] px-3.5 py-3">
        <div className="flex min-w-0 items-center gap-2">
          <div className="flex items-center gap-1.5 rounded-lg bg-[#edf6f2] px-2.5 py-1.5 font-bold tabular-nums text-[#1f6c58]">
            <Clock3 aria-hidden="true" size={13} />
            <span className="text-sm">{horario.hora}</span>
            <span className="text-[9px] font-semibold">{horario.periodo}</span>
          </div>
          <span
            className={`truncate rounded-full px-2.5 py-1 text-[9px] font-bold ${estado.clase}`}
          >
            {estado.etiqueta}
          </span>
        </div>
        <span className="shrink-0 text-[10px] font-semibold tabular-nums text-[#8ba099]">
          #{String(numero).padStart(2, "0")}
        </span>
      </header>

      <div className="space-y-3.5 p-3.5">
        <div className="flex items-center gap-2.5">
          <div className="grid size-9 shrink-0 place-items-center rounded-full bg-[#f7ecdf] text-[#a6662d]">
            <UserRound aria-hidden="true" size={16} />
          </div>
          <div className="min-w-0 flex-1">
            <h2
              id={`viaje-${servicio.id_servicio}`}
              className="truncate text-[13px] font-bold text-[#26423b]"
            >
              {servicio.razon_social_cliente}
            </h2>
            <p className="mt-0.5 text-[10px] text-[#82938c]">
              Servicio #{servicio.id_servicio}
            </p>
          </div>
          <Truck aria-hidden="true" className="shrink-0 text-[#4c907a]" size={17} />
        </div>

        <div className="rounded-xl bg-[#f4f8f6] px-3 py-2.5">
          <div className="flex items-start gap-2">
            <MapPin
              aria-hidden="true"
              className="mt-0.5 shrink-0 text-[#4c907a]"
              size={15}
            />
            <div className="min-w-0">
              <p className="text-[9px] font-bold uppercase tracking-[0.08em] text-[#82978f]">
                Recorrido
              </p>
              <p className="mt-0.5 truncate text-[11px] font-semibold text-[#29443d]">
                {servicio.distancia_ida_km} km de ida
                <span className="px-1.5 text-[#b3c0bb]">·</span>
                {servicio.horas_estimadas} h estimadas
              </p>
            </div>
          </div>
          <div className="mt-2.5 flex items-center gap-2 border-t border-[#e5eeea] pt-2">
            <Truck aria-hidden="true" className="shrink-0 text-[#82978f]" size={13} />
            <p className="truncate text-[10px] text-[#526b62]">
              {servicio.descripcion_tipo_vehiculo}
              {servicio.patente_vehiculo ? ` · ${servicio.patente_vehiculo}` : ""}
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between gap-3 rounded-xl border border-dashed border-[#efc277] bg-[#fff9ed] px-3 py-2.5">
          <span className="text-[10px] font-semibold text-[#94611c]">
            Valor del servicio
          </span>
          <span className="text-[13px] font-bold tabular-nums text-[#87550e]">
            {formatearSaldo(Number(servicio.precio_total))}
          </span>
        </div>
      </div>
    </article>
  );
}
