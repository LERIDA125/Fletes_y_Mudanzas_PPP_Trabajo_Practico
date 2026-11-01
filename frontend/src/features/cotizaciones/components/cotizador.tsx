"use client";

import { Loader2, ReceiptText } from "lucide-react";
import { useRef, useState } from "react";

import { calcularRutaMapa, solicitarCotizacion } from "@/features/servicios/actions";
import { CampoDireccionMapa } from "@/features/servicios/components/campo-direccion-mapa";
import { ResumenCotizacion } from "@/features/servicios/components/resumen-cotizacion";
import type {
  Cotizacion,
  DireccionOpcion,
  ResultadoRuta,
  SolicitudCotizacion,
  TipoVehiculoOpcion,
} from "@/features/servicios/types";

const condicionesIniciales = {
  requiere_ayudante: false,
  acceso_escalera: false,
  zona_concurrida: false,
  urgencia_mismo_dia: false,
};

const controlesCondiciones = [
  ["requiere_ayudante", "Requiere ayudante"],
  ["acceso_escalera", "Acceso por escalera"],
  ["zona_concurrida", "Zona concurrida"],
  ["urgencia_mismo_dia", "Urgencia para el mismo día"],
] as const;

type Propiedades = {
  tiposVehiculo: TipoVehiculoOpcion[];
};

export function Cotizador({ tiposVehiculo }: Propiedades) {
  const [idTipo, setIdTipo] = useState(String(tiposVehiculo[0]?.id ?? ""));
  const [horas, setHoras] = useState("2");
  const [condiciones, setCondiciones] = useState(condicionesIniciales);
  const [origen, setOrigen] = useState<DireccionOpcion | null>(null);
  const [destino, setDestino] = useState<DireccionOpcion | null>(null);
  const [ruta, setRuta] = useState<ResultadoRuta | null>(null);
  const [calculandoRuta, setCalculandoRuta] = useState(false);
  const [errorRuta, setErrorRuta] = useState("");
  const [resultado, setResultado] = useState<Cotizacion | null>(null);
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);
  const solicitudRuta = useRef(0);
  const solicitudCotizacion = useRef(0);

  const sinTipos = tiposVehiculo.length === 0;
  const tiempoRuta = ruta ? formatearDuracion(Number(ruta.duracion_segundos)) : null;

  function invalidarCotizacion() {
    solicitudCotizacion.current += 1;
    setResultado(null);
    setMensaje("");
    setCargando(false);
  }

  function invalidarRuta() {
    solicitudRuta.current += 1;
    setRuta(null);
    setErrorRuta("");
    setCalculandoRuta(false);
    invalidarCotizacion();
  }

  async function calcularRuta(
    puntoOrigen: DireccionOpcion,
    puntoDestino: DireccionOpcion,
  ) {
    const idSolicitud = solicitudRuta.current + 1;
    solicitudRuta.current = idSolicitud;
    setRuta(null);
    setErrorRuta("");
    setCalculandoRuta(true);
    invalidarCotizacion();

    try {
      const respuesta = await calcularRutaMapa(
        {
          longitud: puntoOrigen.longitud,
          latitud: puntoOrigen.latitud,
        },
        {
          longitud: puntoDestino.longitud,
          latitud: puntoDestino.latitud,
        },
      );
      if (solicitudRuta.current !== idSolicitud) {
        return;
      }
      if (!respuesta.ok) {
        setErrorRuta(respuesta.mensaje);
        return;
      }
      setRuta(respuesta.dato);
    } catch {
      if (solicitudRuta.current === idSolicitud) {
        setErrorRuta(
          "No pudimos calcular la ruta. Revisá las direcciones e intentá de nuevo.",
        );
      }
    } finally {
      if (solicitudRuta.current === idSolicitud) {
        setCalculandoRuta(false);
      }
    }
  }

  function cambiarPunto(
    extremo: "origen" | "destino",
    seleccion: DireccionOpcion | null,
  ) {
    invalidarRuta();
    const nuevoOrigen = extremo === "origen" ? seleccion : origen;
    const nuevoDestino = extremo === "destino" ? seleccion : destino;
    setOrigen(nuevoOrigen);
    setDestino(nuevoDestino);

    if (nuevoOrigen && nuevoDestino) {
      void calcularRuta(nuevoOrigen, nuevoDestino);
    }
  }

  function cambiarCondicion(nombre: keyof typeof condicionesIniciales, valor: boolean) {
    setCondiciones((actuales) => ({ ...actuales, [nombre]: valor }));
    invalidarCotizacion();
  }

  async function cotizar(evento: React.FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    invalidarCotizacion();

    const idTipoNumero = Number(idTipo);
    const horasNumero = Number(horas);
    const distanciaNumero = Number(ruta?.distancia_ida_km);

    if (!idTipoNumero) {
      setMensaje("Elegí un tipo de vehículo.");
      return;
    }
    if (!Number.isFinite(horasNumero) || horasNumero < 1) {
      setMensaje("Las horas deben ser 1 o más.");
      return;
    }
    if (!ruta || !Number.isFinite(distanciaNumero) || distanciaNumero < 0) {
      setMensaje("Elegí un origen y un destino para calcular la ruta antes de cotizar.");
      return;
    }

    const idSolicitud = solicitudCotizacion.current;
    const solicitud: SolicitudCotizacion = {
      id_tipo_vehiculo: idTipoNumero,
      horas_estimadas: horasNumero,
      distancia_ida_km: distanciaNumero,
      ...condiciones,
    };

    setCargando(true);
    setMensaje("");
    try {
      const respuesta = await solicitarCotizacion(solicitud);
      if (solicitudCotizacion.current !== idSolicitud) {
        return;
      }
      if (!respuesta.ok) {
        setMensaje(respuesta.mensaje);
        return;
      }
      setResultado(respuesta.dato);
    } catch {
      if (solicitudCotizacion.current === idSolicitud) {
        setMensaje("No pudimos cotizar el viaje. Revisá los datos e intentá de nuevo.");
      }
    } finally {
      if (solicitudCotizacion.current === idSolicitud) {
        setCargando(false);
      }
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
      <section className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm sm:p-6 dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <div className="flex flex-wrap items-start justify-between gap-3 border-b border-[#edf0f4] pb-5 dark:border-[#1e2c44]">
          <div>
            <h3 className="text-base font-bold text-[#172b4d] dark:text-white">
              Nueva cotización
            </h3>
            <p className="mt-0.5 text-xs text-[#96a2b2] dark:text-[#94a3b8]">
              El importe se calcula en el servidor con las tarifas vigentes.
            </p>
          </div>
          <span className="rounded-full bg-[#e9f8ef] px-3 py-1 text-xs font-semibold text-[#248952] dark:bg-[#163827] dark:text-[#4ade80]">
            Tarifas oficiales
          </span>
        </div>

        {sinTipos ? (
          <p role="status" className="mt-5 text-sm text-[#96a2b2] dark:text-[#94a3b8]">
            Todavía no hay tipos de vehículo activos. Cargalos desde Vehículos para poder
            cotizar.
          </p>
        ) : (
          <form noValidate onSubmit={cotizar} className="mt-5 flex flex-col gap-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-1.5 text-xs font-semibold text-[#62738a] dark:text-[#94a3b8]">
                Tipo de vehículo
                <select
                  value={idTipo}
                  onChange={(evento) => {
                    setIdTipo(evento.target.value);
                    invalidarCotizacion();
                  }}
                  className={claseControl}
                >
                  {tiposVehiculo.map((tipo) => (
                    <option key={tipo.id} value={tipo.id}>
                      {tipo.descripcion}
                    </option>
                  ))}
                </select>
              </label>

              <label className="flex flex-col gap-1.5 text-xs font-semibold text-[#62738a] dark:text-[#94a3b8]">
                Horas estimadas
                <input
                  type="number"
                  min="1"
                  step="0.01"
                  inputMode="decimal"
                  value={horas}
                  onChange={(evento) => {
                    setHoras(evento.target.value);
                    invalidarCotizacion();
                  }}
                  className={claseControl}
                />
              </label>
            </div>

            <fieldset className="rounded-xl border border-[#dfe6ef] bg-[#f8fafc] p-4 dark:border-[#1e2c44] dark:bg-[#0d1626]">
              <legend className="px-1 text-sm font-semibold text-[#172b4d] dark:text-white">
                Recorrido del servicio
              </legend>
              <p className="mb-3 text-xs text-[#62738a] dark:text-[#94a3b8]">
                Buscá cada dirección y elegí un resultado para calcular la distancia de
                ida.
              </p>
              <div className="grid gap-3 sm:grid-cols-2">
                <CampoDireccionMapa
                  id="origen-cotizacion"
                  etiqueta="Origen"
                  seleccion={origen}
                  onSeleccionar={(opcion) => cambiarPunto("origen", opcion)}
                />
                <CampoDireccionMapa
                  id="destino-cotizacion"
                  etiqueta="Destino"
                  seleccion={destino}
                  onSeleccionar={(opcion) => cambiarPunto("destino", opcion)}
                />
              </div>
              <p className="mt-2 text-[11px] text-[#62738a] dark:text-[#94a3b8]">
                Geocodificación y rutas:{" "}
                <a
                  href="https://www.openstreetmap.org/copyright"
                  target="_blank"
                  rel="noreferrer"
                  className="underline underline-offset-2 hover:text-[#172b4d] dark:hover:text-white"
                >
                  © OpenStreetMap contributors
                </a>
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <label
                  htmlFor="distancia_ida_km_cotizacion"
                  className="flex flex-col gap-1.5 text-xs font-semibold text-[#62738a] dark:text-[#94a3b8]"
                >
                  Distancia de ida (km)
                  <input
                    id="distancia_ida_km_cotizacion"
                    type="number"
                    readOnly
                    aria-readonly="true"
                    value={ruta?.distancia_ida_km ?? ""}
                    placeholder="Se calcula al elegir las direcciones"
                    className={claseControl}
                  />
                </label>
                <div className="min-h-10 self-end pb-2 text-sm text-[#62738a] dark:text-[#94a3b8]">
                  {calculandoRuta ? (
                    <span role="status" className="inline-flex items-center gap-2">
                      <Loader2
                        aria-hidden="true"
                        size={16}
                        className="animate-spin motion-reduce:animate-none"
                      />
                      Calculando distancia y tiempo…
                    </span>
                  ) : ruta && tiempoRuta ? (
                    <p role="status" aria-live="polite">
                      Tiempo estimado: <strong>{tiempoRuta}</strong>
                    </p>
                  ) : (
                    <p aria-live="polite">La distancia y el tiempo aparecerán acá.</p>
                  )}
                </div>
              </div>
              {errorRuta ? (
                <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
                  <p role="alert" className="text-sm text-red-700 dark:text-red-300">
                    {errorRuta}
                  </p>
                  {origen && destino ? (
                    <button
                      type="button"
                      disabled={calculandoRuta}
                      onClick={() => void calcularRuta(origen, destino)}
                      className={claseBotonSecundario}
                    >
                      Reintentar cálculo
                    </button>
                  ) : null}
                </div>
              ) : null}
            </fieldset>

            <fieldset className="grid gap-2 rounded-xl border border-[#dfe6ef] bg-[#f8fafc] p-4 sm:grid-cols-2 dark:border-[#1e2c44] dark:bg-[#0d1626]">
              <legend className="px-1 text-sm font-semibold text-[#172b4d] dark:text-white">
                Condiciones del viaje
              </legend>
              {controlesCondiciones.map(([nombre, etiqueta]) => (
                <label
                  key={nombre}
                  className="flex min-h-9 items-center gap-2 text-sm text-[#172b4d] dark:text-[#e2e8f0]"
                >
                  <input
                    type="checkbox"
                    checked={condiciones[nombre]}
                    onChange={(evento) => cambiarCondicion(nombre, evento.target.checked)}
                    className="size-4 accent-[#2165d5]"
                  />
                  <span>{etiqueta}</span>
                </label>
              ))}
            </fieldset>

            <p className="rounded-lg border border-[#dbe7fb] bg-[#f4f8ff] px-3 py-2 text-[11px] leading-relaxed text-[#35527a] dark:border-[#1e3a5f] dark:bg-[#12233d] dark:text-[#bfdbfe]">
              El servidor calcula el precio sugerido con las tarifas y condiciones
              vigentes.
            </p>

            {mensaje ? (
              <p
                role="alert"
                className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 dark:border-[#7f1d1d] dark:bg-[#3b1416] dark:text-red-300"
              >
                {mensaje}
              </p>
            ) : null}

            <div>
              <button
                type="submit"
                disabled={cargando || calculandoRuta || !ruta}
                className="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-[#2165d5] px-4 text-xs font-bold text-white shadow-[0_5px_12px_rgba(33,101,213,0.18)] transition hover:bg-[#1857bd] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2165d5] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-[#2563eb] dark:hover:bg-[#1d4ed8]"
              >
                {cargando ? (
                  <>
                    <Loader2 size={15} className="animate-spin" />
                    <span>Cotizando…</span>
                  </>
                ) : (
                  <>
                    <ReceiptText size={15} />
                    <span>Cotizar con el servidor</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </section>

      <aside className="flex flex-col gap-4">
        {resultado ? (
          <ResumenCotizacion cotizacion={resultado} vigente />
        ) : (
          <section className="rounded-2xl bg-[#172b4d] p-5 text-white shadow-[0_8px_24px_rgba(23,43,77,0.12)] dark:border dark:border-[#1e2c44] dark:bg-[#0a182e]">
            <p className="text-xs text-[#aebed4]">Precio sugerido</p>
            <p className="mt-2 text-3xl font-bold tracking-tight">—</p>
            <p className="mt-5 border-t border-white/10 pt-4 text-xs leading-relaxed text-[#aebed4]">
              Completá el recorrido y las condiciones para ver el desglose de la
              cotización.
            </p>
          </section>
        )}
      </aside>
    </div>
  );
}

function formatearDuracion(segundos: number): string {
  if (!Number.isFinite(segundos)) {
    return "No disponible";
  }

  const minutosTotales = Math.max(0, Math.round(segundos / 60));
  if (minutosTotales === 0) {
    return "menos de 1 min";
  }

  const horas = Math.floor(minutosTotales / 60);
  const minutos = minutosTotales % 60;
  if (horas === 0) {
    return `${minutos} min`;
  }
  return minutos === 0 ? `${horas} h` : `${horas} h ${minutos} min`;
}

const claseControl =
  "rounded-lg border border-[#dfe6ef] bg-white px-3 py-2 text-xs font-normal outline-none focus:border-[#2165d5] dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white";

const claseBotonSecundario =
  "inline-flex min-h-9 items-center justify-center rounded-lg border border-[#dfe6ef] bg-white px-3 text-xs font-semibold text-[#172b4d] transition-colors hover:bg-[#f4f8ff] disabled:cursor-not-allowed disabled:opacity-50 dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white dark:hover:bg-[#16253d]";
