"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { CarFront, MoreHorizontal, Trash2 } from "lucide-react";

import { DialogoConfirmacion } from "@/components/ui/dialogo-confirmacion";
import {
  cambiarEstadoServicio,
  cancelarServicio,
  eliminarServicio,
} from "@/features/servicios/actions";
import type { EstadoServicio, Servicio } from "@/features/servicios/types";
import { useMenuDesplegable } from "@/lib/hooks/use-menu-desplegable";

const ETIQUETAS_ESTADO: Record<EstadoServicio, string> = {
  pendiente: "Pendiente",
  confirmado: "Confirmado",
  "en curso": "En curso",
  finalizado: "Finalizado",
  cobrado: "Cobrado",
  cancelado: "Cancelado",
};

function esEstadoServicio(estado: string): estado is EstadoServicio {
  return Object.hasOwn(ETIQUETAS_ESTADO, estado);
}

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
  cancelado: "border-slate-200 bg-slate-50 text-slate-600",
};

export function FilaServicio({ servicio }: { servicio: Servicio }) {
  const router = useRouter();
  const { abierto, alternar, cerrar, anclaRef, menuRef, estilo } = useMenuDesplegable();
  const [selectorAbierto, setSelectorAbierto] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");
  const [dialogoEliminarAbierto, setDialogoEliminarAbierto] = useState(false);

  const transiciones = servicio.transiciones_validas.filter(esEstadoServicio);
  const puedeCambiarEstado = transiciones.length > 0;
  const [estadoSeleccionado, setEstadoSeleccionado] = useState<EstadoServicio | "">("");
  const [motivoCancelacion, setMotivoCancelacion] = useState("");
  // Las props se refrescan después de guardar: si la transición elegida ya no
  // está disponible, se vuelve a la primera que ofrece el backend.
  const estadoElegido =
    estadoSeleccionado && transiciones.includes(estadoSeleccionado)
      ? estadoSeleccionado
      : (transiciones[0] ?? "");

  const estadoClave = servicio.estado.toLowerCase();
  const claseBadge =
    statusStyles[estadoClave] ?? "border-slate-200 bg-slate-50 text-slate-700";

  function cerrarMenu() {
    cerrar();
    setSelectorAbierto(false);
  }

  async function guardarEstado(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!estadoElegido) {
      return;
    }
    if (estadoElegido === "cancelado" && !motivoCancelacion.trim()) {
      setMensajeError("Indicá el motivo de la cancelación.");
      return;
    }

    setMensajeError("");
    setEnviando(true);
    try {
      const resultado =
        estadoElegido === "cancelado"
          ? await cancelarServicio(servicio.id_servicio, motivoCancelacion)
          : await cambiarEstadoServicio(servicio.id_servicio, estadoElegido);

      if (!resultado.ok) {
        setMensajeError(resultado.mensaje);
        return;
      }
      cerrarMenu();
      setMotivoCancelacion("");
      router.refresh();
    } finally {
      setEnviando(false);
    }
  }

  async function confirmarEliminacion() {
    setMensajeError("");
    setEnviando(true);
    try {
      const resultado = await eliminarServicio(servicio.id_servicio);
      if (!resultado.ok) {
        setDialogoEliminarAbierto(false);
        setMensajeError(resultado.mensaje);
        return;
      }
      setDialogoEliminarAbierto(false);
      cerrarMenu();
      router.refresh();
    } finally {
      setEnviando(false);
    }
  }

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
        <div ref={anclaRef} className="inline-block text-left">
          <button
            type="button"
            aria-label={`Opciones de ${servicio.razon_social_cliente}`}
            aria-expanded={abierto}
            aria-haspopup="true"
            onClick={() => {
              alternar();
              setSelectorAbierto(false);
              setMensajeError("");
            }}
            disabled={enviando}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 disabled:opacity-50"
          >
            <MoreHorizontal className="size-4" />
          </button>

          {abierto ? (
            <div
              ref={menuRef}
              style={estilo}
              aria-label={`Acciones de ${servicio.razon_social_cliente}`}
              className="z-50 rounded-xl border border-slate-200 bg-white p-2 text-left shadow-xl"
            >
              {puedeCambiarEstado ? (
                <button
                  type="button"
                  onClick={() => {
                    setSelectorAbierto((abierto) => !abierto);
                    setMensajeError("");
                  }}
                  className="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Cambiar estado
                </button>
              ) : (
                <p className="px-3 py-2 text-xs text-slate-500">
                  El servicio está en un estado final: no admite más cambios.
                </p>
              )}

              {selectorAbierto ? (
                <form
                  onSubmit={guardarEstado}
                  className="border-t border-slate-100 px-2 py-3"
                >
                  <label
                    htmlFor={`estado-servicio-${servicio.id_servicio}`}
                    className="mb-1 block text-xs font-medium text-slate-500"
                  >
                    Nuevo estado
                  </label>
                  <select
                    id={`estado-servicio-${servicio.id_servicio}`}
                    value={estadoElegido}
                    onChange={(evento) => {
                      const estado = evento.target.value;
                      if (esEstadoServicio(estado)) {
                        setEstadoSeleccionado(estado);
                        setMensajeError("");
                      }
                    }}
                    disabled={enviando}
                    className="w-full rounded-lg border border-slate-200 bg-white px-2.5 py-2 text-sm text-slate-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600"
                  >
                    {transiciones.map((estado) => (
                      <option key={estado} value={estado}>
                        {ETIQUETAS_ESTADO[estado]}
                      </option>
                    ))}
                  </select>

                  {estadoElegido === "cancelado" ? (
                    <div className="mt-2">
                      <label
                        htmlFor={`motivo-cancelacion-${servicio.id_servicio}`}
                        className="mb-1 block text-xs font-medium text-slate-500"
                      >
                        Motivo de la cancelación
                      </label>
                      <textarea
                        id={`motivo-cancelacion-${servicio.id_servicio}`}
                        value={motivoCancelacion}
                        onChange={(evento) => setMotivoCancelacion(evento.target.value)}
                        disabled={enviando}
                        rows={2}
                        maxLength={500}
                        placeholder="Ej. El cliente reprogramó el viaje"
                        className="w-full resize-none rounded-lg border border-slate-200 bg-white px-2.5 py-2 text-sm text-slate-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600"
                      />
                    </div>
                  ) : null}

                  <button
                    type="submit"
                    disabled={enviando}
                    className="mt-2 w-full rounded-lg bg-sky-600 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {enviando
                      ? "Actualizando…"
                      : estadoElegido === "cancelado"
                        ? "Cancelar servicio"
                        : "Actualizar estado"}
                  </button>
                </form>
              ) : null}

              <button
                type="button"
                onClick={() => {
                  cerrarMenu();
                  setDialogoEliminarAbierto(true);
                }}
                disabled={enviando}
                className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
              >
                <Trash2 className="size-4" />
                Eliminar
              </button>
            </div>
          ) : null}
          {mensajeError ? (
            <p
              role="alert"
              className="mt-2 block max-w-72 px-2 text-left text-xs text-red-700"
            >
              {mensajeError}
            </p>
          ) : null}
        </div>

        {dialogoEliminarAbierto ? (
          <DialogoConfirmacion
            titulo="Eliminar servicio"
            descripcion={`¿Eliminar el servicio de ${servicio.razon_social_cliente}? Esta acción no se puede deshacer.`}
            textoConfirmar="Sí, eliminar"
            enviando={enviando}
            onConfirmar={confirmarEliminacion}
            onCancelar={() => setDialogoEliminarAbierto(false)}
          />
        ) : null}
      </td>
    </tr>
  );
}
