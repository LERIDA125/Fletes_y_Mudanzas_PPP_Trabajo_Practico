"use client";

import {
  CheckCircle2,
  Clock,
  LogIn,
  MapPin,
  Play,
  RefreshCw,
  Truck,
  UserRound,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import type { EstadoServicio, Servicio } from "@/features/servicios/types";
import { obtenerUsuarioSesionLocal } from "@/lib/api/auth";
import { ErrorApi } from "@/lib/api/http";
import {
  POLLING_SERVICIOS_CHOFER_MS,
  cambiarEstadoServicio,
  suscribirServiciosChofer,
} from "@/lib/api/servicios";

export default function PaginaPortalChofer() {
  const [servicios, setServicios] = useState<Servicio[]>([]);
  const [cargando, setCargando] = useState(true);
  const [actualizandoId, setActualizandoId] = useState<number | null>(null);
  const [ultimaSincronizacion, setUltimaSincronizacion] = useState<string>("—");
  const [error, setError] = useState<string | null>(null);
  const [idChoferFiltroDemo, setIdChoferFiltroDemo] = useState<number | undefined>(
    undefined,
  );

  const usuarioSesion = obtenerUsuarioSesionLocal();
  const esChoferAutenticado = usuarioSesion?.rol === "chofer";

  useEffect(() => {
    const cancelarSuscripcion = suscribirServiciosChofer(
      (listado) => {
        setServicios(listado.items);
        setCargando(false);
        setError(null);
        setUltimaSincronizacion(
          new Date().toLocaleTimeString("es-AR", {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
          }),
        );
      },
      (err) => {
        setCargando(false);
        if (err instanceof ErrorApi) {
          setError(err.message);
        } else {
          setError("No se pudo sincronizar la agenda del chofer.");
        }
      },
      POLLING_SERVICIOS_CHOFER_MS,
      esChoferAutenticado ? undefined : idChoferFiltroDemo,
    );

    return () => {
      cancelarSuscripcion();
    };
  }, [esChoferAutenticado, idChoferFiltroDemo]);

  async function avanzarEstadoViaje(idServicio: number, nuevoEstado: EstadoServicio) {
    setError(null);
    setActualizandoId(idServicio);
    try {
      const actualizado = await cambiarEstadoServicio(idServicio, nuevoEstado);
      setServicios((prev) =>
        prev.map((item) => (item.id_servicio === idServicio ? actualizado : item)),
      );
    } catch (err) {
      if (err instanceof ErrorApi) {
        setError(err.message);
      } else {
        setError("No se pudo actualizar el estado del viaje.");
      }
    } finally {
      setActualizandoId(null);
    }
  }

  return (
    <div className="min-h-screen bg-[#f4f7fb] pb-14 text-[#172b4d] dark:bg-[#0b1320] dark:text-[#f1f5f9]">
      {/* Barra superior móvil del chofer */}
      <header className="sticky top-0 z-20 border-b border-[#e5eaf2] bg-white/95 px-4 py-4 backdrop-blur-md dark:border-[#1e2c44] dark:bg-[#111c2e]/95">
        <div className="mx-auto flex max-w-xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-2xl bg-[#2165d5] text-white">
              <Truck size={20} strokeWidth={2.4} />
            </div>
            <div>
              <h1 className="text-base font-bold text-[#172b4d] dark:text-white">
                Portal Móvil del Chofer
              </h1>
              <p className="text-xs text-[#6b7a90] dark:text-[#94a3b8]">
                {esChoferAutenticado
                  ? `Chofer: ${usuarioSesion.username} (ID #${usuarioSesion.id_chofer})`
                  : "Vista previa sincronizada en tiempo real"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/login"
              className="inline-flex items-center gap-1.5 rounded-xl border border-[#dde4ee] px-3 py-1.5 text-xs font-semibold text-[#172b4d] hover:bg-[#f4f8ff] dark:border-[#243552] dark:text-slate-200"
            >
              <LogIn size={13} />
              <span>{usuarioSesion ? "Cambiar cuenta" : "Login JWT"}</span>
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto mt-5 max-w-xl space-y-4 px-4">
        {/* Indicador de sincronización en tiempo real */}
        <div className="flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-[#dbe7ff] bg-[#f4f8ff] px-4 py-3 text-xs text-[#1e3a66] dark:border-[#243b61] dark:bg-[#16253d] dark:text-[#bfdbfe]">
          <div className="flex items-center gap-2">
            <RefreshCw size={14} className="animate-spin text-[#2165d5]" />
            <span>
              Sincronización en tiempo real activa (cada{" "}
              {POLLING_SERVICIOS_CHOFER_MS / 1000} s)
            </span>
          </div>
          <span className="font-semibold">Última sync: {ultimaSincronizacion}</span>
        </div>

        {/* Selector de chofer solo cuando se previsualiza con rol admin en modo demo */}
        {!esChoferAutenticado && (
          <div className="rounded-2xl border border-[#e6ebf2] bg-white p-4 text-xs dark:border-[#1e2c44] dark:bg-[#111c2e]">
            <label
              htmlFor="filtro-chofer-demo"
              className="mb-1.5 flex items-center gap-1.5 font-bold text-[#172b4d] dark:text-white"
            >
              <UserRound size={14} className="text-[#2165d5]" />
              <span>Modo Administrador: filtrar vista previa por ID de chofer</span>
            </label>
            <input
              id="filtro-chofer-demo"
              type="number"
              min={1}
              value={idChoferFiltroDemo ?? ""}
              onChange={(e) =>
                setIdChoferFiltroDemo(e.target.value ? Number(e.target.value) : undefined)
              }
              placeholder="Todos los viajes (o ingresá ID de chofer, ej. 1)"
              className="w-full rounded-xl border border-[#dce3ee] bg-[#fafcff] px-3 py-2 text-xs text-[#172b4d] outline-none focus:border-[#2165d5] dark:border-[#243552] dark:bg-[#0f172a] dark:text-white"
            />
          </div>
        )}

        {error && (
          <div
            role="alert"
            className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-700 dark:border-rose-900/50 dark:bg-rose-950/40 dark:text-rose-300"
          >
            {error}
          </div>
        )}

        {cargando ? (
          <div className="rounded-3xl border border-[#e6ebf2] bg-white p-8 text-center text-sm text-[#6b7a90] dark:border-[#1e2c44] dark:bg-[#111c2e]">
            Cargando viajes asignados...
          </div>
        ) : servicios.length === 0 ? (
          <div className="rounded-3xl border border-[#e6ebf2] bg-white p-8 text-center dark:border-[#1e2c44] dark:bg-[#111c2e]">
            <p className="text-sm font-bold text-[#172b4d] dark:text-white">
              No tenés viajes asignados en este momento
            </p>
            <p className="mt-1 text-xs text-[#6b7a90] dark:text-[#94a3b8]">
              En cuanto un administrador te asigne un servicio, aparecerá automáticamente
              en esta pantalla.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {servicios.map((servicio) => {
              const puedeIniciar = servicio.estado === "confirmado";
              const puedeFinalizar = servicio.estado === "en curso";

              return (
                <article
                  key={servicio.id_servicio}
                  className="rounded-3xl border border-[#e6ebf2] bg-white p-5 shadow-xs dark:border-[#1e2c44] dark:bg-[#111c2e]"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <span className="text-[11px] font-bold uppercase tracking-wider text-[#8d9bb0]">
                        Viaje #{servicio.id_servicio} • {servicio.fecha}
                      </span>
                      <h2 className="mt-0.5 text-base font-bold text-[#172b4d] dark:text-white">
                        {servicio.razon_social_cliente}
                      </h2>
                    </div>
                    <span className="rounded-full bg-[#edf4ff] px-3 py-1 text-xs font-bold text-[#2165d5] dark:bg-[#1e3458] dark:text-[#60a5fa]">
                      {servicio.estado}
                    </span>
                  </div>

                  <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-[#5e6e85] dark:text-[#94a3b8]">
                    <div className="flex items-center gap-1.5">
                      <Clock size={14} className="text-[#2165d5]" />
                      <span>
                        Inicio: {servicio.hora_inicio ?? "Jornada completa"} (
                        {servicio.horas_estimadas} h)
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <MapPin size={14} className="text-[#2165d5]" />
                      <span>Distancia ida: {servicio.distancia_ida_km} km</span>
                    </div>
                    <div className="col-span-2 flex items-center gap-1.5">
                      <Truck size={14} className="text-[#2165d5]" />
                      <span>
                        {servicio.descripcion_tipo_vehiculo}
                        {servicio.patente_vehiculo
                          ? ` • Patente ${servicio.patente_vehiculo}`
                          : ""}
                        {servicio.nombre_chofer ? ` • ${servicio.nombre_chofer}` : ""}
                      </span>
                    </div>
                  </div>

                  {(puedeIniciar || puedeFinalizar) && (
                    <div className="mt-4 border-t border-[#eef1f6] pt-3 dark:border-[#1e2c44]">
                      {puedeIniciar && (
                        <button
                          type="button"
                          disabled={actualizandoId === servicio.id_servicio}
                          onClick={() =>
                            avanzarEstadoViaje(servicio.id_servicio, "en curso")
                          }
                          className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#2165d5] px-4 py-2.5 text-xs font-bold text-white shadow-xs transition hover:bg-[#1954b8] disabled:opacity-60"
                        >
                          <Play size={14} />
                          <span>Iniciar viaje (Marcar En curso)</span>
                        </button>
                      )}
                      {puedeFinalizar && (
                        <button
                          type="button"
                          disabled={actualizandoId === servicio.id_servicio}
                          onClick={() =>
                            avanzarEstadoViaje(servicio.id_servicio, "finalizado")
                          }
                          className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-xs font-bold text-white shadow-xs transition hover:bg-emerald-700 disabled:opacity-60"
                        >
                          <CheckCircle2 size={14} />
                          <span>Finalizar viaje</span>
                        </button>
                      )}
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
