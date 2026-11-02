"use client";

import {
  AlertCircle,
  Check,
  CheckCircle2,
  Clock,
  Eye,
  FileText,
  Filter,
  Loader2,
  Search,
  User,
  X,
} from "lucide-react";
import { useState, useTransition } from "react";

import {
  aprobarRendicionAccion,
  observarRendicionAccion,
} from "@/features/servicios/actions";
import type { Servicio } from "@/features/servicios/types";
import { formatearSaldo } from "@/lib/utils/formato";

interface Props {
  serviciosIniciales: Servicio[];
}

export function PanelCajaRendiciones({ serviciosIniciales }: Props) {
  const [servicios, setServicios] = useState(serviciosIniciales);
  const [busqueda, setBusqueda] = useState("");
  const [filtroChofer, setFiltroChofer] = useState<string>("todos");
  const [filtroEstado, setFiltroEstado] = useState<string>("todos");
  const [remitoSeleccionado, setRemitoSeleccionado] = useState<Servicio | null>(null);
  const [servicioObservando, setServicioObservando] = useState<Servicio | null>(null);
  const [motivoObservacion, setMotivoObservacion] = useState("");
  const [pendiente, startTransition] = useTransition();
  const [mensajeExito, setMensajeExito] = useState<string | null>(null);
  const [errorAccion, setErrorAccion] = useState<string | null>(null);

  // Obtener lista única de choferes para el filtro
  const choferesUnicos = Array.from(
    new Set(servicios.map((s) => s.nombre_chofer).filter((c): c is string => Boolean(c))),
  );

  // Servicios finalizados o con estado_rendicion definido
  const serviciosRelevantes = servicios.filter(
    (s) =>
      Boolean(s.estado_rendicion) || s.estado === "finalizado" || s.estado === "cobrado",
  );

  // KPIs
  const pendientes = serviciosRelevantes.filter(
    (s) =>
      s.estado_rendicion === "PENDIENTE" ||
      (s.estado === "finalizado" && !s.estado_rendicion),
  );
  const aprobados = serviciosRelevantes.filter(
    (s) => s.estado_rendicion === "RENDIDO" || s.estado === "cobrado",
  );
  const observados = serviciosRelevantes.filter(
    (s) => s.estado_rendicion === "OBSERVADO",
  );

  const totalEnManoPendiente = pendientes.reduce((acc, s) => {
    const monto =
      s.monto_cobrado_real !== null && s.monto_cobrado_real !== undefined
        ? Number(s.monto_cobrado_real)
        : Number(s.precio_total);
    return acc + monto;
  }, 0);

  const totalAprobado = aprobados.reduce((acc, s) => {
    const monto =
      s.monto_cobrado_real !== null && s.monto_cobrado_real !== undefined
        ? Number(s.monto_cobrado_real)
        : Number(s.precio_total);
    return acc + monto;
  }, 0);

  // Filtrado
  const filtrados = serviciosRelevantes.filter((s) => {
    // Filtro por chofer
    if (filtroChofer !== "todos" && s.nombre_chofer !== filtroChofer) {
      return false;
    }
    // Filtro por estado
    if (filtroEstado === "PENDIENTE" && s.estado_rendicion !== "PENDIENTE") {
      return false;
    }
    if (filtroEstado === "RENDIDO" && s.estado_rendicion !== "RENDIDO") {
      return false;
    }
    if (filtroEstado === "OBSERVADO" && s.estado_rendicion !== "OBSERVADO") {
      return false;
    }
    // Búsqueda libre
    if (busqueda.trim()) {
      const q = busqueda.toLowerCase();
      const matchCliente = s.razon_social_cliente.toLowerCase().includes(q);
      const matchChofer = (s.nombre_chofer ?? "").toLowerCase().includes(q);
      const matchId = String(s.id_servicio).includes(q);
      return matchCliente || matchChofer || matchId;
    }
    return true;
  });

  function handleAprobar(servicio: Servicio) {
    setErrorAccion(null);
    setMensajeExito(null);
    startTransition(async () => {
      const res = await aprobarRendicionAccion(servicio.id_servicio);
      if (res.ok) {
        setServicios((prev) =>
          prev.map((s) => (s.id_servicio === servicio.id_servicio ? res.dato : s)),
        );
        if (remitoSeleccionado?.id_servicio === servicio.id_servicio) {
          setRemitoSeleccionado(res.dato);
        }
        setMensajeExito(
          `Rendición del Viaje #${servicio.id_servicio} aprobada. Saldo conciliado.`,
        );
      } else {
        setErrorAccion(res.mensaje);
      }
    });
  }

  function handleConfirmarObservacion(e: React.FormEvent) {
    e.preventDefault();
    if (!servicioObservando) return;
    if (!motivoObservacion.trim()) {
      setErrorAccion("El motivo de la observación es obligatorio.");
      return;
    }

    const idServicio = servicioObservando.id_servicio;
    setErrorAccion(null);
    setMensajeExito(null);
    startTransition(async () => {
      const res = await observarRendicionAccion(idServicio, motivoObservacion.trim());
      if (res.ok) {
        setServicios((prev) =>
          prev.map((s) => (s.id_servicio === idServicio ? res.dato : s)),
        );
        setServicioObservando(null);
        setMotivoObservacion("");
        setMensajeExito(`Rendición del Viaje #${idServicio} marcada como observada.`);
      } else {
        setErrorAccion(res.mensaje);
      }
    });
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Mensajes de feedback */}
      {mensajeExito && (
        <div
          role="status"
          className="flex items-center justify-between rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800 dark:border-emerald-900/60 dark:bg-emerald-950/40 dark:text-emerald-300"
        >
          <span className="flex items-center gap-2">
            <CheckCircle2 size={16} />
            {mensajeExito}
          </span>
          <button
            type="button"
            onClick={() => setMensajeExito(null)}
            className="text-emerald-600 hover:text-emerald-800"
          >
            <X size={15} />
          </button>
        </div>
      )}

      {errorAccion && (
        <div
          role="alert"
          className="flex items-center justify-between rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-800 dark:border-rose-900/60 dark:bg-rose-950/40 dark:text-rose-300"
        >
          <span className="flex items-center gap-2">
            <AlertCircle size={16} />
            {errorAccion}
          </span>
          <button
            type="button"
            onClick={() => setErrorAccion(null)}
            className="text-rose-600 hover:text-rose-800"
          >
            <X size={15} />
          </button>
        </div>
      )}

      {/* Tarjetas KPI */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-amber-200 bg-[#fffdf8] p-4 shadow-xs dark:border-amber-900/60 dark:bg-amber-950/20">
          <p className="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400">
            Dinero en Mano a Rendir
          </p>
          <p className="mt-2 text-2xl font-black text-amber-900 dark:text-amber-200">
            {formatearSaldo(totalEnManoPendiente)}
          </p>
          <p className="mt-1 text-xs text-amber-700/80">
            {pendientes.length} viajes pendientes de aprobación
          </p>
        </div>

        <div className="rounded-2xl border border-emerald-200 bg-[#f9fdfa] p-4 shadow-xs dark:border-emerald-900/60 dark:bg-emerald-950/20">
          <p className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
            Rendido e Ingresado a Caja
          </p>
          <p className="mt-2 text-2xl font-black text-emerald-900 dark:text-emerald-200">
            {formatearSaldo(totalAprobado)}
          </p>
          <p className="mt-1 text-xs text-emerald-700/80">
            {aprobados.length} viajes conciliados y aprobados
          </p>
        </div>

        <div className="rounded-2xl border border-blue-200 bg-[#f8fbff] p-4 shadow-xs dark:border-blue-900/60 dark:bg-blue-950/20">
          <p className="text-xs font-bold uppercase tracking-wider text-blue-700 dark:text-blue-400">
            Viajes con Remito (POD)
          </p>
          <p className="mt-2 text-2xl font-black text-blue-900 dark:text-blue-200">
            {serviciosRelevantes.filter((s) => Boolean(s.foto_remito_url)).length}
          </p>
          <p className="mt-1 text-xs text-blue-700/80">Comprobantes adjuntos recibidos</p>
        </div>

        <div className="rounded-2xl border border-rose-200 bg-[#fff9f9] p-4 shadow-xs dark:border-rose-900/60 dark:bg-rose-950/20">
          <p className="text-xs font-bold uppercase tracking-wider text-rose-700 dark:text-rose-400">
            Rendiciones Observadas
          </p>
          <p className="mt-2 text-2xl font-black text-rose-900 dark:text-rose-200">
            {observados.length}
          </p>
          <p className="mt-1 text-xs text-rose-700/80">
            Requieren corrección o aclaración
          </p>
        </div>
      </div>

      {/* Barra de filtros y búsqueda */}
      <div className="flex flex-col gap-3 rounded-2xl border border-gray-200 bg-white p-4 shadow-xs sm:flex-row sm:items-center sm:justify-between dark:border-gray-800 dark:bg-[#0f172a]">
        <div className="relative flex-1 max-w-md">
          <Search
            size={16}
            className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-gray-400"
          />
          <input
            type="text"
            placeholder="Buscar por cliente, chofer o # viaje…"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="w-full rounded-xl border border-gray-200 py-2 pr-3 pl-9 text-xs focus:border-[#2165d5] focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-white"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Selector de chofer */}
          <div className="flex items-center gap-1.5">
            <User size={14} className="text-gray-400" />
            <select
              value={filtroChofer}
              onChange={(e) => setFiltroChofer(e.target.value)}
              className="rounded-xl border border-gray-200 bg-white px-2.5 py-1.5 text-xs text-gray-700 focus:border-[#2165d5] focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
            >
              <option value="todos">Todos los choferes</option>
              {choferesUnicos.map((chofer) => (
                <option key={chofer} value={chofer}>
                  {chofer}
                </option>
              ))}
            </select>
          </div>

          {/* Selector de estado de rendición */}
          <div className="flex items-center gap-1.5">
            <Filter size={14} className="text-gray-400" />
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
              className="rounded-xl border border-gray-200 bg-white px-2.5 py-1.5 text-xs text-gray-700 focus:border-[#2165d5] focus:outline-none dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
            >
              <option value="todos">Todos los estados</option>
              <option value="PENDIENTE">Pendientes de Rendición</option>
              <option value="RENDIDO">Aprobadas / Rendidas</option>
              <option value="OBSERVADO">Observadas</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tabla de Rendiciones */}
      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xs dark:border-gray-800 dark:bg-[#0f172a]">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-gray-100 bg-gray-50/75 text-[11px] font-bold uppercase tracking-wider text-gray-500 dark:border-gray-800 dark:bg-gray-900/50 dark:text-gray-400">
              <tr>
                <th className="px-4 py-3">Viaje</th>
                <th className="px-4 py-3">Chofer</th>
                <th className="px-4 py-3">Cliente</th>
                <th className="px-4 py-3">Cotizado</th>
                <th className="px-4 py-3">Cobrado Real</th>
                <th className="px-4 py-3 text-center">Remito (POD)</th>
                <th className="px-4 py-3 text-center">Estado Rendición</th>
                <th className="px-4 py-3 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {filtrados.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-10 text-center text-gray-400">
                    No se encontraron rendiciones para los filtros seleccionados.
                  </td>
                </tr>
              ) : (
                filtrados.map((s) => {
                  const cotizado = Number(s.precio_total);
                  const cobrado =
                    s.monto_cobrado_real !== null && s.monto_cobrado_real !== undefined
                      ? Number(s.monto_cobrado_real)
                      : cotizado;
                  const diferencia = cobrado - cotizado;
                  const estadoRen =
                    s.estado_rendicion ??
                    (s.estado === "cobrado" ? "RENDIDO" : "PENDIENTE");

                  return (
                    <tr
                      key={s.id_servicio}
                      className="hover:bg-gray-50/50 dark:hover:bg-gray-800/40 transition"
                    >
                      <td className="px-4 py-3 font-semibold tabular-nums text-gray-900 dark:text-white">
                        #{s.id_servicio}
                        <span className="block text-[10px] text-gray-400 font-normal">
                          {s.fecha}
                        </span>
                      </td>

                      <td className="px-4 py-3">
                        <span className="font-medium text-gray-800 dark:text-gray-200 flex items-center gap-1.5">
                          <User size={13} className="text-gray-400" />
                          {s.nombre_chofer ?? "Sin chofer"}
                        </span>
                        {s.patente_vehiculo && (
                          <span className="text-[10px] text-gray-400">
                            {s.patente_vehiculo} · {s.descripcion_tipo_vehiculo}
                          </span>
                        )}
                      </td>

                      <td className="px-4 py-3">
                        <span className="font-medium text-gray-900 dark:text-white">
                          {s.razon_social_cliente}
                        </span>
                        <span className="block text-[10px] text-gray-400">
                          {s.distancia_ida_km} km · {s.horas_estimadas} hs
                        </span>
                      </td>

                      <td className="px-4 py-3 tabular-nums text-gray-600 dark:text-gray-300">
                        {formatearSaldo(cotizado)}
                      </td>

                      <td className="px-4 py-3">
                        <span className="font-bold tabular-nums text-gray-900 dark:text-white">
                          {formatearSaldo(cobrado)}
                        </span>
                        {diferencia !== 0 && (
                          <span
                            className={`block text-[10px] font-semibold tabular-nums ${
                              diferencia > 0 ? "text-emerald-600" : "text-amber-600"
                            }`}
                          >
                            {diferencia > 0 ? "+" : ""}
                            {formatearSaldo(diferencia)}
                          </span>
                        )}
                      </td>

                      <td className="px-4 py-3 text-center">
                        {s.foto_remito_url ? (
                          <button
                            type="button"
                            onClick={() => setRemitoSeleccionado(s)}
                            className="inline-flex items-center gap-1 rounded-lg border border-[#b2d5c7] bg-[#f0f8f5] px-2.5 py-1 text-[11px] font-bold text-[#1f6c58] hover:bg-[#e0f1eb] transition dark:border-emerald-800 dark:bg-emerald-950/30 dark:text-emerald-400"
                          >
                            <Eye size={12} />
                            Ver foto
                          </button>
                        ) : (
                          <span className="text-[10px] text-gray-400">Sin foto</span>
                        )}
                      </td>

                      <td className="px-4 py-3 text-center">
                        {estadoRen === "PENDIENTE" && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-0.5 text-[10px] font-bold text-amber-800 dark:bg-amber-950/40 dark:text-amber-300">
                            <Clock size={11} />
                            Pendiente
                          </span>
                        )}
                        {estadoRen === "RENDIDO" && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-[10px] font-bold text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">
                            <CheckCircle2 size={11} />
                            Rendido
                          </span>
                        )}
                        {estadoRen === "OBSERVADO" && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-rose-100 px-2.5 py-0.5 text-[10px] font-bold text-rose-800 dark:bg-rose-950/40 dark:text-rose-300">
                            <AlertCircle size={11} />
                            Observado
                          </span>
                        )}
                      </td>

                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {estadoRen !== "RENDIDO" ? (
                            <>
                              <button
                                type="button"
                                disabled={pendiente}
                                onClick={() => handleAprobar(s)}
                                className="inline-flex items-center gap-1 rounded-lg bg-[#1f6c58] px-3 py-1.5 text-xs font-bold text-white shadow-xs hover:bg-[#185848] transition disabled:opacity-50"
                              >
                                <Check size={13} />
                                Aprobar
                              </button>
                              <button
                                type="button"
                                disabled={pendiente}
                                onClick={() => {
                                  setServicioObservando(s);
                                  setMotivoObservacion(s.observacion_rendicion ?? "");
                                }}
                                className="inline-flex items-center gap-1 rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 transition"
                              >
                                Observar
                              </button>
                            </>
                          ) : (
                            <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                              <CheckCircle2 size={13} />
                              Conciliado
                            </span>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal para Ver Foto del Remito en Pantalla Completa */}
      {remitoSeleccionado && remitoSeleccionado.foto_remito_url && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-xs animate-in fade-in"
          onClick={() => setRemitoSeleccionado(null)}
        >
          <div
            className="relative max-h-[92vh] max-w-3xl w-full rounded-2xl bg-white p-5 shadow-2xl dark:bg-gray-900 border border-gray-200 dark:border-gray-800 flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-gray-800 shrink-0">
              <div>
                <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <FileText size={18} className="text-[#1f6c58]" />
                  Prueba de Entrega (POD) — Viaje #{remitoSeleccionado.id_servicio}
                </h3>
                <p className="text-xs text-gray-500">
                  Chofer: <strong>{remitoSeleccionado.nombre_chofer}</strong> · Cliente:{" "}
                  <strong>{remitoSeleccionado.razon_social_cliente}</strong>
                </p>
              </div>
              <button
                type="button"
                onClick={() => setRemitoSeleccionado(null)}
                className="rounded-full p-1.5 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <X size={20} />
              </button>
            </div>

            <div className="my-3 overflow-hidden rounded-xl bg-black/5 flex-1 flex items-center justify-center min-h-[350px]">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={remitoSeleccionado.foto_remito_url}
                alt={`Remito del viaje #${remitoSeleccionado.id_servicio}`}
                className="max-h-[60vh] w-full object-contain"
              />
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-gray-100 dark:border-gray-800 shrink-0">
              <div className="text-xs">
                <span className="text-gray-500">Efectivo Cobrado Declarado:</span>{" "}
                <span className="font-bold text-emerald-700 text-sm">
                  {formatearSaldo(
                    remitoSeleccionado.monto_cobrado_real !== null &&
                      remitoSeleccionado.monto_cobrado_real !== undefined
                      ? Number(remitoSeleccionado.monto_cobrado_real)
                      : Number(remitoSeleccionado.precio_total),
                  )}
                </span>
              </div>

              <div className="flex items-center gap-2 w-full sm:w-auto">
                {remitoSeleccionado.estado_rendicion !== "RENDIDO" ? (
                  <button
                    type="button"
                    disabled={pendiente}
                    onClick={() => handleAprobar(remitoSeleccionado)}
                    className="flex-1 sm:flex-none inline-flex items-center justify-center gap-2 rounded-xl bg-[#1f6c58] px-4 py-2.5 text-xs font-bold text-white shadow-sm hover:bg-[#185848] transition disabled:opacity-50"
                  >
                    {pendiente ? (
                      <Loader2 size={14} className="animate-spin" />
                    ) : (
                      <Check size={15} />
                    )}
                    Aprobar Rendición
                  </button>
                ) : (
                  <span className="text-xs font-bold text-emerald-600 flex items-center gap-1">
                    <CheckCircle2 size={15} />
                    Rendición ya aprobada
                  </span>
                )}
                <button
                  type="button"
                  onClick={() => setRemitoSeleccionado(null)}
                  className="rounded-xl border border-gray-200 px-4 py-2.5 text-xs font-semibold text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal para Observar Rendición */}
      {servicioObservando && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs animate-in fade-in"
          onClick={() => setServicioObservando(null)}
        >
          <div
            className="w-full max-w-md rounded-2xl bg-white p-5 shadow-2xl dark:bg-gray-900 border border-gray-200 dark:border-gray-800"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <AlertCircle size={18} className="text-rose-600" />
              Observar Rendición — Viaje #{servicioObservando.id_servicio}
            </h3>
            <p className="mt-1 text-xs text-gray-500">
              Indicá el motivo por el cual no se aprueba la rendición del chofer{" "}
              <strong>{servicioObservando.nombre_chofer}</strong>.
            </p>

            <form onSubmit={handleConfirmarObservacion} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-bold text-gray-700 dark:text-gray-300 mb-1">
                  Motivo de la observación
                </label>
                <textarea
                  rows={3}
                  required
                  value={motivoObservacion}
                  onChange={(e) => setMotivoObservacion(e.target.value)}
                  placeholder="Ej: Falta firma legible en el remito, diferencia en monto cobrado…"
                  className="w-full rounded-xl border border-gray-200 p-3 text-xs focus:border-[#2165d5] focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setServicioObservando(null)}
                  disabled={pendiente}
                  className="rounded-xl border border-gray-200 px-4 py-2 text-xs font-semibold text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={pendiente || !motivoObservacion.trim()}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-rose-600 px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-rose-700 disabled:opacity-50"
                >
                  {pendiente ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <AlertCircle size={14} />
                  )}
                  Registrar Observación
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
