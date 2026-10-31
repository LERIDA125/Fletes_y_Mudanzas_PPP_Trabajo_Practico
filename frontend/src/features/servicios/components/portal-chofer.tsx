"use client";

import { CalendarDays, CircleDollarSign, Truck } from "lucide-react";
import { useEffect, useState } from "react";

import { BotonCerrarSesion } from "@/features/auth/components/boton-cerrar-sesion";
import { obtenerServiciosChofer } from "@/features/servicios/actions";
import { TarjetaViajeChofer } from "@/features/servicios/components/tarjeta-viaje-chofer";
import type { Servicio } from "@/features/servicios/types";

const INTERVALO_ACTUALIZACION_MS = 10_000;
const ZONA_HORARIA = "America/Argentina/Buenos_Aires";

function obtenerFechaArgentina(fecha: Date): string {
  const partes = new Intl.DateTimeFormat("en", {
    timeZone: ZONA_HORARIA,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(fecha);
  const parte = (tipo: string) => partes.find((item) => item.type === tipo)?.value ?? "";

  return `${parte("year")}-${parte("month")}-${parte("day")}`;
}

function etiquetaFecha(fecha: string): string {
  const mediodia = new Date(`${fecha}T12:00:00`);
  const etiqueta = new Intl.DateTimeFormat("es-AR", {
    timeZone: ZONA_HORARIA,
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(mediodia);

  return etiqueta.charAt(0).toUpperCase() + etiqueta.slice(1);
}

function ordenarServicios(servicios: Servicio[]): Servicio[] {
  return [...servicios].sort((a, b) => {
    const ordenFecha = a.fecha.localeCompare(b.fecha);
    if (ordenFecha !== 0) return ordenFecha;

    const ordenHora = (a.hora_inicio ?? "23:59").localeCompare(b.hora_inicio ?? "23:59");
    return ordenHora || a.id_servicio - b.id_servicio;
  });
}

export function PortalChofer({
  nombre,
  fechaInicial,
  serviciosIniciales,
  errorInicial,
}: {
  nombre: string;
  fechaInicial: string;
  serviciosIniciales: Servicio[];
  errorInicial: string | null;
}) {
  const [servicios, setServicios] = useState(serviciosIniciales);
  const [fechaHoy, setFechaHoy] = useState(fechaInicial);
  const [mensajeError, setMensajeError] = useState(errorInicial);
  const [actualizando, setActualizando] = useState(false);

  useEffect(() => {
    let desmontado = false;
    let temporizador: ReturnType<typeof setTimeout>;

    async function actualizarViajes() {
      setActualizando(true);
      const resultado = await obtenerServiciosChofer();

      if (desmontado) return;
      if (resultado.ok) {
        setServicios(resultado.dato);
        setMensajeError(null);
        setFechaHoy(obtenerFechaArgentina(new Date()));
      } else {
        setMensajeError(resultado.mensaje);
      }

      setActualizando(false);
      temporizador = setTimeout(actualizarViajes, INTERVALO_ACTUALIZACION_MS);
    }

    temporizador = setTimeout(actualizarViajes, INTERVALO_ACTUALIZACION_MS);

    return () => {
      desmontado = true;
      clearTimeout(temporizador);
    };
  }, []);

  const viajesDeHoy = ordenarServicios(
    servicios.filter((servicio) => servicio.fecha === fechaHoy),
  );

  return (
    <div className="h-dvh overflow-hidden bg-[#e3eeea] px-0 text-[#24423a] sm:px-4 sm:py-5">
      <div className="mx-auto flex h-full min-h-0 w-full max-w-[430px] flex-col overflow-hidden bg-[#f7faf8] shadow-[0_18px_50px_-25px_rgba(24,62,54,0.42)] sm:h-[min(900px,calc(100dvh-2.5rem))] sm:rounded-[2rem] sm:ring-1 sm:ring-[#b6cbc3]">
        <header
          id="agenda"
          className="shrink-0 bg-[#193f3a] px-5 pt-[calc(env(safe-area-inset-top)+1.2rem)] pb-4 text-white"
        >
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[10px] font-medium text-[#c5ddd5]">
                {etiquetaFecha(fechaHoy)}
              </p>
              <h1 className="mt-1.5 text-[21px] font-bold tracking-[-0.035em]">
                Hola, {nombre}
              </h1>
              <p className="mt-3 flex items-center gap-2 text-[11px] text-[#deeee8]">
                <span className="grid size-5 place-items-center rounded-full bg-[#f2b35e] text-[#573b17]">
                  <Truck aria-hidden="true" size={11} />
                </span>
                Tu jornada está en marcha
              </p>
            </div>
            <BotonCerrarSesion />
          </div>
        </header>

        <main className="min-h-0 flex-1 overflow-y-auto px-3.5 pt-4 pb-5">
          <section id="viajes" aria-labelledby="titulo-viajes">
            <div className="mb-3.5 flex items-end justify-between gap-3 px-1">
              <div>
                <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-[#7b958b]">
                  Agenda del día
                </p>
                <h2
                  id="titulo-viajes"
                  className="mt-1 text-[17px] font-bold tracking-[-0.03em] text-[#24463d]"
                >
                  Tus viajes de hoy
                </h2>
              </div>
              <span className="mb-0.5 shrink-0 rounded-full bg-[#dcefe8] px-2.5 py-1 text-[9px] font-bold text-[#26735e]">
                {viajesDeHoy.length} {viajesDeHoy.length === 1 ? "viaje" : "viajes"}
              </span>
            </div>

            {mensajeError ? (
              <div
                role="alert"
                className="mb-3 rounded-xl border border-[#efc4b8] bg-[#fff3ef] px-3.5 py-3 text-xs leading-5 text-[#8c4135]"
              >
                {mensajeError}
              </div>
            ) : null}

            {viajesDeHoy.length > 0 ? (
              <div className="space-y-3">
                {viajesDeHoy.map((servicio, indice) => (
                  <TarjetaViajeChofer
                    key={servicio.id_servicio}
                    servicio={servicio}
                    numero={indice + 1}
                    onActualizado={(actualizado) => {
                      setServicios((prev) =>
                        prev.map((s) =>
                          s.id_servicio === actualizado.id_servicio ? actualizado : s,
                        ),
                      );
                    }}
                  />
                ))}
              </div>
            ) : mensajeError ? null : (
              <div className="rounded-2xl border border-dashed border-[#cbdcd5] bg-white px-5 py-9 text-center">
                <div className="mx-auto grid size-11 place-items-center rounded-full bg-[#e8f3ee] text-[#4c8874]">
                  <CalendarDays aria-hidden="true" size={20} />
                </div>
                <h3 className="mt-3 text-sm font-bold text-[#29483f]">
                  Hoy no tenés viajes asignados
                </h3>
                <p className="mx-auto mt-1 max-w-[250px] text-xs leading-5 text-[#7f938a]">
                  Cuando te asignen un servicio, vas a verlo en esta agenda.
                </p>
              </div>
            )}
          </section>
        </main>

        <nav
          aria-label="Navegación del chofer"
          className="shrink-0 border-t border-[#e6eeea] bg-white px-3 pt-2 pb-[calc(env(safe-area-inset-bottom)+0.4rem)]"
        >
          <ul className="grid grid-cols-3">
            <li>
              <a
                href="#agenda"
                className="flex min-h-12 flex-col items-center justify-center gap-1 rounded-xl text-[#91a49c] transition-colors hover:bg-[#f4f8f6] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#28745f]"
              >
                <CalendarDays aria-hidden="true" size={15} />
                <span className="text-[9px] font-semibold">Agenda</span>
              </a>
            </li>
            <li>
              <a
                href="#viajes"
                aria-current="location"
                className="flex min-h-12 flex-col items-center justify-center gap-1 rounded-xl bg-[#e8f4ef] text-[#28745f] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#28745f]"
              >
                <Truck aria-hidden="true" size={16} />
                <span className="text-[9px] font-bold">Viajes de hoy</span>
              </a>
            </li>
            <li>
              <button
                type="button"
                disabled
                title="Rendiciones todavía no disponibles"
                className="flex min-h-12 w-full flex-col items-center justify-center gap-1 rounded-xl text-[#a4b2ac] disabled:cursor-not-allowed"
              >
                <CircleDollarSign aria-hidden="true" size={15} />
                <span className="text-[9px] font-semibold">Rendiciones</span>
              </button>
            </li>
          </ul>
          <p className="sr-only" aria-live="polite">
            {actualizando ? "Actualizando viajes" : ""}
          </p>
        </nav>
      </div>
    </div>
  );
}
