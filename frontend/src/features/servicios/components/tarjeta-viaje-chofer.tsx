"use client";

import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Clock3,
  Eye,
  FileText,
  Loader2,
  MapPin,
  Play,
  Truck,
  UserRound,
  X,
} from "lucide-react";
import { useState, useTransition } from "react";

import { iniciarViajeChofer } from "@/features/servicios/actions";
import { ModalFinalizarViaje } from "@/features/servicios/components/modal-finalizar-viaje";
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
  alActualizar,
}: {
  servicio: Servicio;
  numero: number;
  alActualizar?: () => void;
}) {
  const [modalFinalizar, setModalFinalizar] = useState(false);
  const [modalFotoRemito, setModalFotoRemito] = useState(false);
  const [iniciandoViaje, startTransition] = useTransition();
  const [errorAccion, setErrorAccion] = useState<string | null>(null);

  const horario = horaConPeriodo(servicio.hora_inicio);
  const estado = ESTADOS[servicio.estado] ?? ESTADOS.pendiente;

  function handleIniciarViaje() {
    setErrorAccion(null);
    startTransition(async () => {
      const res = await iniciarViajeChofer(servicio.id_servicio);
      if (res.ok) {
        if (alActualizar) alActualizar();
      } else {
        setErrorAccion(res.mensaje);
      }
    });
  }

  return (
    <>
      <article
        aria-labelledby={`viaje-${servicio.id_servicio}`}
        className="overflow-hidden rounded-[1.2rem] border border-[#dce9e4] bg-white shadow-[0_8px_24px_-20px_rgba(27,65,57,0.5)] transition"
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
                {servicio.patente_vehiculo
                  ? `${servicio.patente_vehiculo} · ${servicio.descripcion_tipo_vehiculo}`
                  : servicio.descripcion_tipo_vehiculo}
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

          {/* Información y estado de rendición (H10) */}
          {(servicio.estado === "finalizado" || servicio.estado === "cobrado") && (
            <div className="rounded-xl border border-emerald-200/80 bg-emerald-50/50 p-2.5 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-[#1e463a] flex items-center gap-1">
                  <CheckCircle2 size={13} className="text-emerald-600" />
                  Rendición de Caja:
                </span>
                {servicio.estado_rendicion === "PENDIENTE" && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-800">
                    <Clock size={11} />
                    Pendiente
                  </span>
                )}
                {servicio.estado_rendicion === "RENDIDO" && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                    <CheckCircle2 size={11} />
                    Aprobada
                  </span>
                )}
                {servicio.estado_rendicion === "OBSERVADO" && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-rose-100 px-2 py-0.5 text-[10px] font-bold text-rose-800">
                    <AlertCircle size={11} />
                    Observada
                  </span>
                )}
              </div>

              {servicio.monto_cobrado_real !== null &&
                servicio.monto_cobrado_real !== undefined && (
                  <p className="text-[11px] text-emerald-900 flex items-center justify-between">
                    <span>Cobrado real:</span>
                    <strong className="font-bold">
                      {formatearSaldo(Number(servicio.monto_cobrado_real))}
                    </strong>
                  </p>
                )}

              {servicio.observacion_rendicion && (
                <p className="rounded-lg bg-rose-50 p-1.5 text-[10px] text-rose-800 border border-rose-200">
                  <strong>Observación admin:</strong> {servicio.observacion_rendicion}
                </p>
              )}

              {servicio.foto_remito_url && (
                <button
                  type="button"
                  onClick={() => setModalFotoRemito(true)}
                  className="w-full inline-flex items-center justify-center gap-1.5 rounded-lg border border-[#a2cfbe] bg-white py-1.5 text-[11px] font-bold text-[#1f6c58] hover:bg-[#edf6f2] transition"
                >
                  <Eye size={13} />
                  Ver Remito Firmado
                </button>
              )}
            </div>
          )}

          {errorAccion && (
            <div
              role="alert"
              className="rounded-xl border border-rose-200 bg-rose-50 p-2.5 text-xs text-rose-700"
            >
              {errorAccion}
            </div>
          )}

          {/* Botones de acción operativa del chofer */}
          <div className="pt-1">
            {servicio.estado === "confirmado" && (
              <button
                type="button"
                onClick={handleIniciarViaje}
                disabled={iniciandoViaje}
                className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-[#28745f] py-2.5 text-xs font-bold text-white shadow-sm hover:bg-[#1e5849] active:scale-98 transition disabled:opacity-60"
              >
                {iniciandoViaje ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    Iniciando viaje…
                  </>
                ) : (
                  <>
                    <Play size={14} className="fill-white" />
                    Iniciar Viaje (En Camino)
                  </>
                )}
              </button>
            )}

            {servicio.estado === "en curso" && (
              <button
                type="button"
                onClick={() => setModalFinalizar(true)}
                className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-[#1a4a40] py-3 text-xs font-bold text-white shadow-md hover:bg-[#13372f] active:scale-98 transition"
              >
                <CheckCircle2 size={16} className="text-emerald-400" />
                Finalizar Viaje y Rendir Remito
              </button>
            )}
          </div>
        </div>
      </article>

      {/* Modal para finalizar viaje con captura de remito y monto cobrado */}
      {modalFinalizar && (
        <ModalFinalizarViaje
          servicio={servicio}
          abierto={modalFinalizar}
          alCerrar={() => setModalFinalizar(false)}
          alFinalizar={() => {
            if (alActualizar) alActualizar();
          }}
        />
      )}

      {/* Modal para ver la foto del remito en pantalla completa */}
      {modalFotoRemito && servicio.foto_remito_url && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-3 sm:p-6 backdrop-blur-xs animate-in fade-in"
          onClick={() => setModalFotoRemito(false)}
        >
          <div
            className="relative max-h-[90vh] max-w-2xl w-full rounded-2xl bg-white p-4 shadow-2xl dark:bg-gray-900"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-gray-800">
              <h3 className="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <FileText size={16} className="text-[#1f6c58]" />
                Comprobante de Remito Firmado (Viaje #{servicio.id_servicio})
              </h3>
              <button
                type="button"
                onClick={() => setModalFotoRemito(false)}
                className="rounded-full p-1.5 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <X size={18} />
              </button>
            </div>
            <div className="mt-3 overflow-hidden rounded-xl bg-black/5 flex items-center justify-center">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={servicio.foto_remito_url}
                alt={`Remito firmado de ${servicio.razon_social_cliente}`}
                className="max-h-[70vh] w-full object-contain"
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
