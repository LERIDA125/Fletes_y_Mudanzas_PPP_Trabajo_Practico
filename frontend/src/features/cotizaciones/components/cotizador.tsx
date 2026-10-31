"use client";

import { CircleDollarSign, Loader2, ReceiptText } from "lucide-react";
import { useState } from "react";

import { solicitarCotizacion } from "@/features/servicios/actions";
import type { Cotizacion, TipoVehiculoOpcion } from "@/features/servicios/types";

const formatoMoneda = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
});

const formatoCantidad = new Intl.NumberFormat("es-AR", {
  maximumFractionDigits: 2,
});

type Propiedades = {
  tiposVehiculo: TipoVehiculoOpcion[];
};

export function Cotizador({ tiposVehiculo }: Propiedades) {
  const [idTipo, setIdTipo] = useState(String(tiposVehiculo[0]?.id ?? ""));
  const [horas, setHoras] = useState("2");
  const [distancia, setDistancia] = useState("18");
  const [resultado, setResultado] = useState<Cotizacion | null>(null);
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);

  const sinTipos = tiposVehiculo.length === 0;

  function cambiarDatos() {
    setResultado(null);
  }

  async function cotizar(evento: React.FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setMensaje("");
    setResultado(null);

    const idTipoNumero = Number(idTipo);
    const horasNumero = Number(horas);
    const distanciaNumero = Number(distancia);

    if (!idTipoNumero) {
      setMensaje("Elegí un tipo de vehículo.");
      return;
    }
    if (!Number.isFinite(horasNumero) || horasNumero < 1) {
      setMensaje("Las horas deben ser 1 o más.");
      return;
    }
    if (!Number.isFinite(distanciaNumero) || distanciaNumero < 0) {
      setMensaje("La distancia no puede ser negativa.");
      return;
    }

    setCargando(true);
    try {
      const respuesta = await solicitarCotizacion({
        id_tipo_vehiculo: idTipoNumero,
        horas_estimadas: horasNumero,
        distancia_ida_km: distanciaNumero,
      });
      if (!respuesta.ok) {
        setMensaje(respuesta.mensaje);
        return;
      }
      setResultado(respuesta.dato);
    } finally {
      setCargando(false);
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
                    cambiarDatos();
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
                    cambiarDatos();
                  }}
                  className={claseControl}
                />
              </label>

              <label className="flex flex-col gap-1.5 text-xs font-semibold text-[#62738a] sm:col-span-2 dark:text-[#94a3b8]">
                Distancia de ida (km)
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  inputMode="decimal"
                  value={distancia}
                  onChange={(evento) => {
                    setDistancia(evento.target.value);
                    cambiarDatos();
                  }}
                  className={claseControl}
                />
              </label>
            </div>

            <p className="rounded-lg border border-[#dbe7fb] bg-[#f4f8ff] px-3 py-2 text-[11px] leading-relaxed text-[#35527a] dark:border-[#1e3a5f] dark:bg-[#12233d] dark:text-[#bfdbfe]">
              El servidor duplica la distancia de ida y aplica la franquicia de kilómetros
              configurada. El resultado es el precio oficial del servicio.
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
                disabled={cargando}
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
        <section className="rounded-2xl bg-[#172b4d] p-5 text-white shadow-[0_8px_24px_rgba(23,43,77,0.12)] dark:border dark:border-[#1e2c44] dark:bg-[#0a182e]">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-[#aebed4]">Total cotizado</p>
              <p className="mt-2 text-3xl font-bold tracking-tight">
                {resultado ? formatoMoneda.format(Number(resultado.precio_final)) : "—"}
              </p>
            </div>
            <div className="grid size-10 place-items-center rounded-xl bg-white/10">
              <CircleDollarSign size={20} />
            </div>
          </div>

          {resultado ? (
            <div className="mt-5 flex flex-col gap-2 border-t border-white/10 pt-4 text-xs text-[#c5d1e1]">
              <div className="flex justify-between gap-4">
                <span>Tipo de vehículo</span>
                <span className="text-right font-semibold text-white">
                  {resultado.descripcion_tipo_vehiculo}
                </span>
              </div>
              <div className="flex justify-between gap-4">
                <span>Horas estimadas</span>
                <span className="font-semibold text-white">
                  {formatoCantidad.format(Number(resultado.horas_estimadas))}
                </span>
              </div>
              <div className="flex justify-between gap-4">
                <span>Distancia total</span>
                <span className="font-semibold text-white">
                  {formatoCantidad.format(Number(resultado.distancia_total_km))} km
                </span>
              </div>
              <div className="flex justify-between gap-4">
                <span>Km excedente</span>
                <span className="font-semibold text-white">
                  {formatoCantidad.format(Number(resultado.km_excedente))} km
                </span>
              </div>
              <div className="flex justify-between gap-4">
                <span>Tarifa por hora</span>
                <span className="font-semibold text-white">
                  {formatoMoneda.format(Number(resultado.tarifa_hora_base))}
                </span>
              </div>
              <div className="flex justify-between gap-4">
                <span>Tarifa por km excedente</span>
                <span className="font-semibold text-white">
                  {formatoMoneda.format(Number(resultado.tarifa_km_excedente))}
                </span>
              </div>
            </div>
          ) : (
            <p className="mt-5 border-t border-white/10 pt-4 text-xs leading-relaxed text-[#aebed4]">
              Completá los datos y cotizá para ver el desglose oficial que devuelve el
              sistema.
            </p>
          )}
        </section>
      </aside>
    </div>
  );
}

const claseControl =
  "rounded-lg border border-[#dfe6ef] bg-white px-3 py-2 text-xs font-normal outline-none focus:border-[#2165d5] dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white";
