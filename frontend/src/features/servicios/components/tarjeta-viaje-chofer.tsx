"use client";

import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  ExternalLink,
  FileCheck2,
  Image as ImageIcon,
  Loader2,
  MapPin,
  Play,
  Truck,
  UserRound,
  X,
} from "lucide-react";
import { useState } from "react";

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

const ESTADOS_RENDICION_BADGE: Record<
  string,
  { etiqueta: string; clase: string; icono: typeof Clock3 }
> = {
  PENDIENTE: {
    etiqueta: "Pendiente de rendición",
    clase: "bg-[#fff3cd] text-[#856404] border-[#ffeeba]",
    icono: Clock3,
  },
  RENDIDO: {
    etiqueta: "Rendido y Aprobado",
    clase: "bg-[#d4edda] text-[#155724] border-[#c3e6cb]",
    icono: CheckCircle2,
  },
  OBSERVADO: {
    etiqueta: "Observado",
    clase: "bg-[#f8d7da] text-[#721c24] border-[#f5c6cb]",
    icono: AlertTriangle,
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
  servicio: servicioInicial,
  numero,
  onActualizado,
}: {
  servicio: Servicio;
  numero: number;
  onActualizado?: (actualizado: Servicio) => void;
}) {
  const [servicio, setServicio] = useState<Servicio>(servicioInicial);
  const [modalFinalizarAbierto, setModalFinalizarAbierto] = useState(false);
  const [modalFotoRemitoAbierto, setModalFotoRemitoAbierto] = useState(false);
  const [iniciandoViaje, setIniciandoViaje] = useState(false);
  const [errorAccion, setErrorAccion] = useState<string | null>(null);

  // Mantener actualizado el estado local si el padre le pasa uno nuevo
  if (servicio.id_servicio !== servicioInicial.id_servicio) {
    setServicio(servicioInicial);
  }

  const horario = horaConPeriodo(servicio.hora_inicio);
  const estado = ESTADOS[servicio.estado] ?? ESTADOS.pendiente;
  const rendicionBadge = servicio.estado_rendicion
    ? ESTADOS_RENDICION_BADGE[servicio.estado_rendicion]
    : null;

  async function handleIniciarViaje() {
    setErrorAccion(null);
    setIniciandoViaje(true);
    try {
      const resultado = await iniciarViajeChofer(servicio.id_servicio);
      if (resultado.ok) {
        setServicio(resultado.dato);
        onActualizado?.(resultado.dato);
      } else {
        setErrorAccion(resultado.mensaje);
      }
    } catch {
      setErrorAccion("No se pudo iniciar el viaje. Verificá tu conexión.");
    } finally {
      setIniciandoViaje(false);
    }
  }

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
              {servicio.patente_vehiculo
                ? `${servicio.patente_vehiculo} · ${servicio.descripcion_tipo_vehiculo}`
                : servicio.descripcion_tipo_vehiculo}
            </p>
          </div>
        </div>

        {/* Sección económica: Cotizado vs. Monto Cobrado Real */}
        <div className="space-y-1.5 rounded-xl border border-dashed border-[#efc277] bg-[#fff9ed] p-2.5">
          <div className="flex items-center justify-between gap-3">
            <span className="text-[10px] font-semibold text-[#94611c]">
              Tarifa cotizada
            </span>
            <span className="text-[12px] font-bold tabular-nums text-[#87550e]">
              {formatearSaldo(Number(servicio.precio_total))}
            </span>
          </div>

          {servicio.monto_cobrado_real !== null &&
            servicio.monto_cobrado_real !== undefined && (
              <div className="flex items-center justify-between gap-3 border-t border-[#f4dfb8] pt-1.5">
                <span className="text-[10px] font-bold text-[#1f6c58]">
                  Cobrado en mano
                </span>
                <span className="text-[13px] font-black tabular-nums text-[#1f6c58]">
                  {formatearSaldo(Number(servicio.monto_cobrado_real))}
                </span>
              </div>
            )}
        </div>

        {/* Estado de Rendición (si el viaje ya fue cerrado) */}
        {rendicionBadge && (
          <div
            className={`flex flex-col gap-1 rounded-xl border px-3 py-2 text-xs ${rendicionBadge.clase}`}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="flex items-center gap-1.5 font-bold text-[11px]">
                <rendicionBadge.icono size={13} />
                <span>{rendicionBadge.etiqueta}</span>
              </span>
              {servicio.foto_remito_url && (
                <button
                  type="button"
                  onClick={() => setModalFotoRemitoAbierto(true)}
                  className="flex items-center gap-1 text-[10px] font-semibold underline hover:opacity-80"
                >
                  <ImageIcon size={12} />
                  <span>Ver remito</span>
                </button>
              )}
            </div>
            {servicio.observacion_rendicion && (
              <p className="text-[10px] font-medium leading-4 opacity-90">
                Nota: {servicio.observacion_rendicion}
              </p>
            )}
          </div>
        )}

        {errorAccion && (
          <p className="rounded-lg bg-red-50 p-2 text-center text-xs font-semibold text-red-600">
            {errorAccion}
          </p>
        )}

        {/* Botonera de acciones operativas para el Chofer */}
        <div className="flex flex-col gap-2 pt-1">
          {servicio.estado === "confirmado" && (
            <button
              type="button"
              onClick={handleIniciarViaje}
              disabled={iniciandoViaje}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#28745f] py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-[#1f5c4b] disabled:opacity-50"
            >
              {iniciandoViaje ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  <span>Iniciando viaje...</span>
                </>
              ) : (
                <>
                  <Play size={14} fill="currentColor" />
                  <span>Iniciar viaje</span>
                </>
              )}
            </button>
          )}

          {(servicio.estado === "en curso" || servicio.estado === "confirmado") && (
            <button
              type="button"
              onClick={() => setModalFinalizarAbierto(true)}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#a76312] py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-[#884e0b]"
            >
              <FileCheck2 size={15} />
              <span>Finalizar Viaje y Rendir</span>
            </button>
          )}
        </div>
      </div>

      {/* Modal de Finalización y POD */}
      <ModalFinalizarViaje
        servicio={servicio}
        abierto={modalFinalizarAbierto}
        onCerrar={() => setModalFinalizarAbierto(false)}
        onExito={(actualizado) => {
          setServicio(actualizado);
          onActualizado?.(actualizado);
        }}
      />

      {/* Modal visor de foto de remito en tamaño completo */}
      {modalFotoRemitoAbierto && servicio.foto_remito_url && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-xs"
        >
          <div className="relative max-h-[90vh] max-w-xl overflow-hidden rounded-2xl bg-black">
            <button
              type="button"
              onClick={() => setModalFotoRemitoAbierto(false)}
              className="absolute top-3 right-3 z-10 rounded-full bg-black/60 p-2 text-white hover:bg-black/90"
              aria-label="Cerrar visor"
            >
              <X size={18} />
            </button>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={servicio.foto_remito_url}
              alt={`Remito firmado del servicio #${servicio.id_servicio}`}
              className="max-h-[85vh] w-auto object-contain"
            />
          </div>
        </div>
      )}
    </article>
  );
}
