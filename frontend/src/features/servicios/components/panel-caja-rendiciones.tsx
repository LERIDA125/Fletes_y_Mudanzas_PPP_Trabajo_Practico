"use client";

import {
  AlertCircle,
  AlertTriangle,
  ArrowDownToLine,
  Check,
  CheckCircle2,
  Clock3,
  DollarSign,
  Eye,
  FileText,
  Filter,
  Loader2,
  MessageSquare,
  Search,
  User,
  X,
} from "lucide-react";
import { useState, useTransition } from "react";

import {
  aprobarRendicionServicio,
  observarRendicionServicio,
} from "@/features/servicios/actions";
import type { Servicio } from "@/features/servicios/types";
import { formatearSaldo } from "@/lib/utils/formato";

interface PanelCajaRendicionesProps {
  serviciosIniciales: Servicio[];
}

export function PanelCajaRendiciones({ serviciosIniciales }: PanelCajaRendicionesProps) {
  const [servicios, setServicios] = useState<Servicio[]>(serviciosIniciales);
  const [busqueda, setBusqueda] = useState("");
  const [filtroChofer, setFiltroChofer] = useState<string>("todos");
  const [filtroEstado, setFiltroEstado] = useState<string>("PENDIENTES");
  const [servicioSeleccionado, setServicioSeleccionado] = useState<Servicio | null>(null);
  const [servicioAObservar, setServicioAObservar] = useState<Servicio | null>(null);
  const [textoObservacion, setTextoObservacion] = useState("");
  const [mensajeError, setMensajeError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  // Filtrar servicios relevantes para Caja y Rendiciones (finalizados, cobrados o con estado_rendicion)
  const serviciosRendicion = servicios.filter(
    (s) => s.estado_rendicion || s.estado === "finalizado" || s.estado === "cobrado",
  );

  // Obtener lista única de choferes para el dropdown de filtro
  const choferesUnicos = Array.from(
    new Set(
      serviciosRendicion
        .map((s) => s.nombre_chofer)
        .filter((nombre): nombre is string => Boolean(nombre)),
    ),
  );

  // KPIs Financieros Reales
  const totalPendiente = serviciosRendicion
    .filter((s) => s.estado_rendicion === "PENDIENTE")
    .reduce((sum, s) => sum + Number(s.monto_cobrado_real || s.precio_total || 0), 0);

  const totalRendido = serviciosRendicion
    .filter((s) => s.estado_rendicion === "RENDIDO")
    .reduce((sum, s) => sum + Number(s.monto_cobrado_real || s.precio_total || 0), 0);

  const cantidadPendientes = serviciosRendicion.filter(
    (s) => s.estado_rendicion === "PENDIENTE",
  ).length;

  const cantidadObservados = serviciosRendicion.filter(
    (s) => s.estado_rendicion === "OBSERVADO",
  ).length;

  // Filtrado de la tabla
  const serviciosFiltrados = serviciosRendicion.filter((s) => {
    // Filtro por estado
    if (filtroEstado === "PENDIENTES" && s.estado_rendicion !== "PENDIENTE") {
      return false;
    }
    if (filtroEstado === "OBSERVADOS" && s.estado_rendicion !== "OBSERVADO") {
      return false;
    }
    if (filtroEstado === "RENDIDOS" && s.estado_rendicion !== "RENDIDO") {
      return false;
    }

    // Filtro por chofer
    if (filtroChofer !== "todos" && s.nombre_chofer !== filtroChofer) {
      return false;
    }

    // Filtro por búsqueda textual
    if (!busqueda) return true;
    const query = busqueda.toLowerCase();
    const idCoincide = String(s.id_servicio).includes(query);
    const clienteCoincide = s.razon_social_cliente.toLowerCase().includes(query);
    const choferCoincide = (s.nombre_chofer || "").toLowerCase().includes(query);
    return idCoincide || clienteCoincide || choferCoincide;
  });

  function handleAprobar(idServicio: number) {
    setMensajeError(null);
    startTransition(async () => {
      const res = await aprobarRendicionServicio(idServicio);
      if (res.ok) {
        setServicios((prev) =>
          prev.map((s) => (s.id_servicio === idServicio ? res.dato : s)),
        );
        if (servicioSeleccionado?.id_servicio === idServicio) {
          setServicioSeleccionado(res.dato);
        }
      } else {
        setMensajeError(res.mensaje);
      }
    });
  }

  function handleGuardarObservacion(e: React.FormEvent) {
    e.preventDefault();
    if (!servicioAObservar) return;

    setMensajeError(null);
    startTransition(async () => {
      const res = await observarRendicionServicio(
        servicioAObservar.id_servicio,
        textoObservacion,
      );
      if (res.ok) {
        setServicios((prev) =>
          prev.map((s) =>
            s.id_servicio === servicioAObservar.id_servicio ? res.dato : s,
          ),
        );
        setServicioAObservar(null);
        setTextoObservacion("");
      } else {
        setMensajeError(res.mensaje);
      }
    });
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
            Control financiero
          </p>
          <h1 className="text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            Caja y Rendiciones
          </h1>
          <p className="mt-1 text-xs text-[#7f8da1] dark:text-[#94a3b8]">
            Revisá los comprobantes de remito firmado (POD) y conciliá los montos cobrados
            en mano.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => {
              // Exportar simple CSV de los servicios filtrados
              const encabezados =
                "ID,Fecha,Chofer,Cliente,Cotizado,CobradoReal,EstadoRendicion\n";
              const filas = serviciosFiltrados
                .map(
                  (s) =>
                    `"${s.id_servicio}","${s.fecha}","${s.nombre_chofer || "Sin chofer"}","${s.razon_social_cliente}","${s.precio_total}","${s.monto_cobrado_real || s.precio_total}","${s.estado_rendicion || "SIN RENDICION"}"`,
                )
                .join("\n");
              const blob = new Blob([encabezados + filas], {
                type: "text/csv;charset=utf-8;",
              });
              const url = URL.createObjectURL(blob);
              const enlace = document.createElement("a");
              enlace.href = url;
              enlace.setAttribute(
                "download",
                `rendiciones-${new Date().toISOString().slice(0, 10)}.csv`,
              );
              document.body.appendChild(enlace);
              enlace.click();
              document.body.removeChild(enlace);
            }}
            className="flex items-center gap-1.5 rounded-xl border border-[#dfe6ef] bg-white px-3.5 py-2.5 text-xs font-semibold text-[#62738a] shadow-xs hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:bg-[#111c2e] dark:text-[#cbd5e1] dark:hover:bg-[#16253d]"
          >
            <ArrowDownToLine size={15} />
            <span>Exportar CSV</span>
          </button>
        </div>
      </div>

      {mensajeError && (
        <div
          role="alert"
          className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-xs font-semibold text-red-700 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300"
        >
          <AlertCircle size={16} className="shrink-0" />
          <span>{mensajeError}</span>
        </div>
      )}

      {/* Tarjetas KPI Financieras */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
          <p className="text-xs font-medium text-[#8b99ab] dark:text-[#94a3b8]">
            Pendiente de rendición
          </p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-[#b86a16] sm:text-3xl dark:text-[#fbbf24]">
            {formatearSaldo(totalPendiente)}
          </p>
          <p className="mt-1 text-xs font-medium text-[#8b99ab] dark:text-[#94a3b8]">
            {cantidadPendientes}{" "}
            {cantidadPendientes === 1 ? "viaje a conciliar" : "viajes a conciliar"}
          </p>
        </div>

        <div className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
          <p className="text-xs font-medium text-[#8b99ab] dark:text-[#94a3b8]">
            Total rendido y cobrado
          </p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-[#248952] sm:text-3xl dark:text-[#4ade80]">
            {formatearSaldo(totalRendido)}
          </p>
          <p className="mt-1 text-xs font-medium text-[#248952] dark:text-[#4ade80]">
            Saldos ingresados a la caja
          </p>
        </div>

        <div className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
          <p className="text-xs font-medium text-[#8b99ab] dark:text-[#94a3b8]">
            Viajes observados
          </p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-[#d9383a] sm:text-3xl dark:text-[#f87171]">
            {cantidadObservados}
          </p>
          <p className="mt-1 text-xs font-medium text-[#8b99ab] dark:text-[#94a3b8]">
            Requieren revisión con el chofer
          </p>
        </div>
      </div>

      {/* Filtros y Tabla */}
      <section className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm sm:p-6 dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-[#edf0f4] pb-4 dark:border-[#1e2c44]">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold text-[#172b4d] dark:text-white">
              Mostrar:
            </span>
            <div className="flex rounded-xl border border-[#dfe6ef] bg-[#fbfcfd] p-1 dark:border-[#1e2c44] dark:bg-[#0d1626]">
              <button
                type="button"
                onClick={() => setFiltroEstado("PENDIENTES")}
                className={`rounded-lg px-3 py-1 text-xs font-semibold transition ${
                  filtroEstado === "PENDIENTES"
                    ? "bg-[#2165d5] text-white shadow-xs"
                    : "text-[#62738a] hover:text-[#172b4d] dark:text-[#94a3b8] dark:hover:text-white"
                }`}
              >
                Pendientes ({cantidadPendientes})
              </button>
              <button
                type="button"
                onClick={() => setFiltroEstado("OBSERVADOS")}
                className={`rounded-lg px-3 py-1 text-xs font-semibold transition ${
                  filtroEstado === "OBSERVADOS"
                    ? "bg-[#d9383a] text-white shadow-xs"
                    : "text-[#62738a] hover:text-[#172b4d] dark:text-[#94a3b8] dark:hover:text-white"
                }`}
              >
                Observados ({cantidadObservados})
              </button>
              <button
                type="button"
                onClick={() => setFiltroEstado("RENDIDOS")}
                className={`rounded-lg px-3 py-1 text-xs font-semibold transition ${
                  filtroEstado === "RENDIDOS"
                    ? "bg-[#248952] text-white shadow-xs"
                    : "text-[#62738a] hover:text-[#172b4d] dark:text-[#94a3b8] dark:hover:text-white"
                }`}
              >
                Rendidos
              </button>
              <button
                type="button"
                onClick={() => setFiltroEstado("TODOS")}
                className={`rounded-lg px-3 py-1 text-xs font-semibold transition ${
                  filtroEstado === "TODOS"
                    ? "bg-[#64748b] text-white shadow-xs"
                    : "text-[#62738a] hover:text-[#172b4d] dark:text-[#94a3b8] dark:hover:text-white"
                }`}
              >
                Todos
              </button>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Filtro Chofer */}
            <div className="flex items-center gap-1.5 rounded-xl border border-[#dfe6ef] bg-[#fbfcfd] px-2.5 py-1.5 dark:border-[#1e2c44] dark:bg-[#0d1626]">
              <User size={13} className="text-[#99a7b8]" />
              <select
                value={filtroChofer}
                onChange={(e) => setFiltroChofer(e.target.value)}
                className="bg-transparent text-xs text-[#172b4d] outline-none dark:text-white"
              >
                <option value="todos">Todos los choferes</option>
                {choferesUnicos.map((ch) => (
                  <option key={ch} value={ch}>
                    {ch}
                  </option>
                ))}
              </select>
            </div>

            {/* Búsqueda */}
            <div className="flex items-center gap-2 rounded-xl border border-[#dfe6ef] bg-[#fbfcfd] px-3 py-1.5 dark:border-[#1e2c44] dark:bg-[#0d1626]">
              <Search size={14} className="text-[#99a7b8] dark:text-[#64748b]" />
              <input
                type="text"
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                placeholder="Buscar por cliente o chofer..."
                className="w-48 bg-transparent text-xs text-[#172b4d] outline-none placeholder:text-[#aab4c1] dark:text-white dark:placeholder:text-[#64748b]"
              />
            </div>
          </div>
        </div>

        {/* Tabla */}
        <div className="overflow-x-auto">
          <table className="w-full min-w-[850px] text-left text-xs">
            <thead>
              <tr className="border-b border-[#f0f2f5] text-[10px] font-bold uppercase tracking-wider text-[#a0adbd] dark:border-[#1e2c44] dark:text-[#64748b]">
                <th className="px-3 py-3">Servicio</th>
                <th className="px-3 py-3">Chofer Asignado</th>
                <th className="px-3 py-3">Cliente / Fecha</th>
                <th className="px-3 py-3 text-right">Cotizado</th>
                <th className="px-3 py-3 text-right">Cobrado Real</th>
                <th className="px-3 py-3 text-center">Remito (POD)</th>
                <th className="px-3 py-3">Estado Rendición</th>
                <th className="px-3 py-3 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {serviciosFiltrados.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-xs text-[#8b99ab]">
                    No se encontraron viajes para conciliar en este filtro.
                  </td>
                </tr>
              ) : (
                serviciosFiltrados.map((s) => {
                  const tieneDiferencia =
                    s.monto_cobrado_real !== null &&
                    s.monto_cobrado_real !== undefined &&
                    Number(s.monto_cobrado_real) !== Number(s.precio_total);

                  return (
                    <tr
                      key={s.id_servicio}
                      className="border-b border-[#f1f3f6] text-xs transition hover:bg-[#fafcff] last:border-0 dark:border-[#1e2c44] dark:hover:bg-[#16253d]"
                    >
                      <td className="px-3 py-3.5 font-bold text-[#2165d5] dark:text-[#60a5fa]">
                        #SRV-{s.id_servicio}
                      </td>
                      <td className="px-3 py-3.5 font-semibold text-[#172b4d] dark:text-white">
                        {s.nombre_chofer || (
                          <span className="italic text-[#8b99ab]">Sin chofer</span>
                        )}
                      </td>
                      <td className="px-3 py-3.5">
                        <p className="font-semibold text-[#172b4d] dark:text-white">
                          {s.razon_social_cliente}
                        </p>
                        <p className="text-[10px] text-[#718096] dark:text-[#94a3b8]">
                          {s.fecha}{" "}
                          {s.hora_inicio ? `· ${s.hora_inicio.slice(0, 5)}` : ""}
                        </p>
                      </td>
                      <td className="px-3 py-3.5 text-right font-medium text-[#718096] dark:text-[#94a3b8]">
                        {formatearSaldo(Number(s.precio_total))}
                      </td>
                      <td className="px-3 py-3.5 text-right font-bold text-[#172b4d] dark:text-white">
                        {s.monto_cobrado_real !== null &&
                        s.monto_cobrado_real !== undefined ? (
                          <span
                            className={
                              tieneDiferencia ? "text-[#b86a16] dark:text-[#fbbf24]" : ""
                            }
                          >
                            {formatearSaldo(Number(s.monto_cobrado_real))}
                          </span>
                        ) : (
                          <span className="text-[#8b99ab]">-</span>
                        )}
                      </td>
                      <td className="px-3 py-3.5 text-center">
                        {s.foto_remito_url ? (
                          <button
                            type="button"
                            onClick={() => setServicioSeleccionado(s)}
                            className="inline-flex items-center gap-1 rounded-lg border border-[#cbe4d8] bg-[#f2f9f5] px-2 py-1 text-[11px] font-bold text-[#1f6c58] hover:bg-[#e4f3ec] dark:border-[#164e3c] dark:bg-[#0c281f] dark:text-[#4ade80]"
                          >
                            <Eye size={12} />
                            <span>Ver foto</span>
                          </button>
                        ) : (
                          <span className="text-[10px] text-[#8b99ab]">Sin foto</span>
                        )}
                      </td>
                      <td className="px-3 py-3.5">
                        {s.estado_rendicion === "PENDIENTE" && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-[#fff4e5] px-2.5 py-0.5 text-[10px] font-bold text-[#b86a16] dark:bg-[#3d2914] dark:text-[#fbbf24]">
                            <Clock3 size={11} /> Pendiente
                          </span>
                        )}
                        {s.estado_rendicion === "RENDIDO" && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-[#e9f8ef] px-2.5 py-0.5 text-[10px] font-bold text-[#248952] dark:bg-[#163827] dark:text-[#4ade80]">
                            <CheckCircle2 size={11} /> Rendido
                          </span>
                        )}
                        {s.estado_rendicion === "OBSERVADO" && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-[#fde8e8] px-2.5 py-0.5 text-[10px] font-bold text-[#d9383a] dark:bg-[#3d1414] dark:text-[#f87171]">
                            <AlertTriangle size={11} /> Observado
                          </span>
                        )}
                        {!s.estado_rendicion && (
                          <span className="text-[10px] text-[#8b99ab]">-</span>
                        )}
                      </td>
                      <td className="px-3 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {s.estado_rendicion !== "RENDIDO" && (
                            <>
                              <button
                                type="button"
                                onClick={() => {
                                  setServicioAObservar(s);
                                  setTextoObservacion(s.observacion_rendicion || "");
                                }}
                                disabled={isPending}
                                title="Observar rendición"
                                className="rounded-lg p-1.5 text-[#b86a16] hover:bg-[#fff4e5] dark:text-[#fbbf24] dark:hover:bg-[#3d2914]"
                              >
                                <MessageSquare size={14} />
                              </button>
                              <button
                                type="button"
                                onClick={() => handleAprobar(s.id_servicio)}
                                disabled={isPending}
                                className="inline-flex items-center gap-1 rounded-lg bg-[#248952] px-2.5 py-1.5 text-[11px] font-bold text-white shadow-xs hover:bg-[#1e7244] disabled:opacity-50"
                              >
                                {isPending ? (
                                  <Loader2 size={12} className="animate-spin" />
                                ) : (
                                  <Check size={12} />
                                )}
                                <span>Aprobar</span>
                              </button>
                            </>
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
      </section>

      {/* Modal Visor de Comprobante / Remito Firmado */}
      {servicioSeleccionado && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs"
        >
          <div className="w-full max-w-xl overflow-hidden rounded-2xl bg-white shadow-2xl dark:border dark:border-[#1e2c44] dark:bg-[#111c2e]">
            <header className="flex items-start justify-between border-b border-[#edf0f4] p-4 dark:border-[#1e2c44]">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
                  Prueba de Entrega (POD)
                </span>
                <h3 className="text-base font-bold text-[#172b4d] dark:text-white">
                  Remito de viaje #SRV-{servicioSeleccionado.id_servicio}
                </h3>
                <p className="text-xs text-[#7f8da1] dark:text-[#94a3b8]">
                  Chofer: {servicioSeleccionado.nombre_chofer || "Sin chofer"} · Cliente:{" "}
                  {servicioSeleccionado.razon_social_cliente}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setServicioSeleccionado(null)}
                className="rounded-lg p-1.5 text-[#8b99ab] hover:bg-[#f3f5f8] dark:hover:bg-[#18263d]"
              >
                <X size={18} />
              </button>
            </header>

            <div className="flex flex-col gap-4 p-5">
              {/* Imagen del Remito */}
              <div className="max-h-[50vh] overflow-hidden rounded-xl border border-[#dfe6ef] bg-black/5 dark:border-[#1e2c44]">
                {servicioSeleccionado.foto_remito_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={servicioSeleccionado.foto_remito_url}
                    alt="Remito firmado"
                    className="max-h-[50vh] w-full object-contain"
                  />
                ) : (
                  <div className="py-12 text-center text-xs text-[#8b99ab]">
                    No se adjuntó imagen del remito para este viaje.
                  </div>
                )}
              </div>

              {/* Detalle de conciliación */}
              <div className="grid grid-cols-2 gap-3 rounded-xl border border-[#e8edf4] bg-[#f8fbff] p-3 text-xs dark:border-[#1e2c44] dark:bg-[#0d1626]">
                <div>
                  <span className="text-[#8b99ab] dark:text-[#64748b]">
                    Cotización calculada:
                  </span>
                  <p className="text-sm font-bold text-[#172b4d] dark:text-white">
                    {formatearSaldo(Number(servicioSeleccionado.precio_total))}
                  </p>
                </div>
                <div>
                  <span className="text-[#8b99ab] dark:text-[#64748b]">
                    Monto cobrado declarado:
                  </span>
                  <p className="text-sm font-black text-[#1f6c58] dark:text-[#4ade80]">
                    {formatearSaldo(
                      Number(
                        servicioSeleccionado.monto_cobrado_real ??
                          servicioSeleccionado.precio_total,
                      ),
                    )}
                  </p>
                </div>
              </div>

              {servicioSeleccionado.observacion_rendicion && (
                <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-300">
                  <span className="font-bold">Observación registrada:</span>
                  <p className="mt-0.5">{servicioSeleccionado.observacion_rendicion}</p>
                </div>
              )}
            </div>

            <footer className="flex items-center justify-end gap-2 border-t border-[#edf0f4] p-4 dark:border-[#1e2c44]">
              <button
                type="button"
                onClick={() => setServicioSeleccionado(null)}
                className="rounded-lg border border-[#dfe6ef] px-4 py-2 text-xs font-semibold text-[#62738a] hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:text-[#94a3b8] dark:hover:bg-[#16253d]"
              >
                Cerrar
              </button>
              {servicioSeleccionado.estado_rendicion !== "RENDIDO" && (
                <button
                  type="button"
                  onClick={() => {
                    handleAprobar(servicioSeleccionado.id_servicio);
                    setServicioSeleccionado(null);
                  }}
                  disabled={isPending}
                  className="rounded-lg bg-[#248952] px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-[#1e7244]"
                >
                  Aprobar Rendición
                </button>
              )}
            </footer>
          </div>
        </div>
      )}

      {/* Modal para Observar Rendición */}
      {servicioAObservar && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs"
        >
          <div className="w-full max-w-md rounded-2xl bg-white p-5 shadow-2xl dark:border dark:border-[#1e2c44] dark:bg-[#111c2e]">
            <header className="flex items-start justify-between border-b border-[#edf0f4] pb-3 dark:border-[#1e2c44]">
              <div>
                <h3 className="text-sm font-bold text-[#172b4d] dark:text-white">
                  Observar rendición #SRV-{servicioAObservar.id_servicio}
                </h3>
                <p className="text-xs text-[#7f8da1] dark:text-[#94a3b8]">
                  Indicá el motivo por el cual se pone en revisión este viaje.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setServicioAObservar(null)}
                className="rounded-lg p-1 text-[#8b99ab] hover:bg-[#f3f5f8] dark:hover:bg-[#18263d]"
              >
                <X size={16} />
              </button>
            </header>

            <form onSubmit={handleGuardarObservacion} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#172b4d] dark:text-white">
                  Observación administrativa <span className="text-red-500">*</span>
                </label>
                <textarea
                  rows={3}
                  value={textoObservacion}
                  onChange={(e) => setTextoObservacion(e.target.value)}
                  placeholder="Ej: Falta ticket de peaje, o hay una diferencia de $5.000 sin justificar..."
                  required
                  maxLength={255}
                  className="mt-1.5 w-full rounded-xl border border-[#dfe6ef] p-3 text-xs outline-none focus:border-[#2165d5] dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setServicioAObservar(null)}
                  className="rounded-lg border border-[#dfe6ef] px-3.5 py-2 text-xs font-semibold text-[#62738a] hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:text-[#94a3b8]"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isPending || !textoObservacion.trim()}
                  className="flex items-center gap-1 rounded-lg bg-[#d9383a] px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-[#b82d2f] disabled:opacity-50"
                >
                  {isPending && <Loader2 size={12} className="animate-spin" />}
                  <span>Guardar Observación</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
