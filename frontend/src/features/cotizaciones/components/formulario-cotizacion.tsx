"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

import { calcularCotizacion } from "@/features/cotizaciones/actions";
import type {
  Cotizacion,
  SolicitudCotizacion,
  TipoVehiculoCotizacion,
} from "@/features/cotizaciones/types";
import type { DatosCotizacion } from "@/features/cotizaciones/schemas/cotizacion";

import { ResumenCotizacion } from "@/features/servicios/components/resumen-cotizacion";

const TIEMPO_DE_ESPERA_MS = 350;

type CamposCotizacion = keyof DatosCotizacion | "precio_acordado";

type Propiedades = {
  tiposVehiculo: TipoVehiculoCotizacion[];
  datos: DatosCotizacion;
  onDatosChange: (parcial: Partial<DatosCotizacion>) => void;
  precioAcordado?: string;
  onPrecioAcordadoChange?: (valor: string, manual: boolean) => void;
  onCotizacionChange?: (cotizacion: Cotizacion | null) => void;
  errores?: Partial<Record<CamposCotizacion, string>>;
  incluirPrecioAcordado?: boolean;
};

function solicitudDe(datos: DatosCotizacion): SolicitudCotizacion | null {
  const idTipoVehiculo = Number(datos.id_tipo_vehiculo);
  const horas = Number(String(datos.horas_estimadas ?? "").replace(",", "."));
  const km = Number(String(datos.km_estimados ?? "").replace(",", "."));
  if (
    !Number.isInteger(idTipoVehiculo) ||
    idTipoVehiculo <= 0 ||
    !Number.isFinite(horas) ||
    horas < 1 ||
    !Number.isFinite(km) ||
    km < 0
  ) {
    return null;
  }
  return {
    id_tipo_vehiculo: idTipoVehiculo,
    horas_estimadas: horas,
    km_estimados: km,
    requiere_ayudante: Boolean(datos.requiere_ayudante),
    acceso_escalera: Boolean(datos.acceso_escalera),
    zona_concurrida: Boolean(datos.zona_concurrida),
    urgencia_mismo_dia: Boolean(datos.urgencia_mismo_dia),
  };
}

export function FormularioCotizacion({
  tiposVehiculo,
  datos,
  onDatosChange,
  precioAcordado = "",
  onPrecioAcordadoChange,
  onCotizacionChange,
  errores = {},
  incluirPrecioAcordado = true,
}: Propiedades) {
  const [cotizacion, setCotizacion] = useState<Cotizacion | null>(null);
  const [calculando, setCalculando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const temporizador = useRef<ReturnType<typeof setTimeout> | null>(null);
  const solicitudEnCurso = useRef(0);
  const editadoManualmente = useRef(false);

  useEffect(() => {
    return () => {
      if (temporizador.current) {
        clearTimeout(temporizador.current);
      }
      solicitudEnCurso.current += 1;
    };
  }, []);

  function agendar(valores: DatosCotizacion) {
    if (temporizador.current) {
      clearTimeout(temporizador.current);
      temporizador.current = null;
    }

    const numeroDeSolicitud = solicitudEnCurso.current + 1;
    solicitudEnCurso.current = numeroDeSolicitud;
    setCotizacion(null);
    onCotizacionChange?.(null);
    setMensaje("");
    if (!editadoManualmente.current) {
      onPrecioAcordadoChange?.("", false);
    }

    const solicitud = solicitudDe(valores);
    if (!solicitud) {
      setCalculando(false);
      return;
    }

    setCalculando(true);
    temporizador.current = setTimeout(async () => {
      try {
        const respuesta = await calcularCotizacion(solicitud);
        if (solicitudEnCurso.current !== numeroDeSolicitud) {
          return;
        }
        if (!respuesta.ok) {
          setMensaje(respuesta.mensaje);
          return;
        }

        setCotizacion(respuesta.dato);
        onCotizacionChange?.(respuesta.dato);
        if (!editadoManualmente.current) {
          onPrecioAcordadoChange?.(respuesta.dato.precio_sugerido, false);
        }
      } catch (error) {
        if (!(error instanceof Error)) {
          throw error;
        }
        if (solicitudEnCurso.current !== numeroDeSolicitud) {
          return;
        }
        setMensaje(
          error.message ||
            "No pudimos calcular el precio sugerido. Revisá los datos e intentá de nuevo.",
        );
      } finally {
        if (solicitudEnCurso.current === numeroDeSolicitud) {
          setCalculando(false);
        }
      }
    }, TIEMPO_DE_ESPERA_MS);
  }

  function cambiar(parcial: Partial<DatosCotizacion>) {
    const nuevosDatos = { ...datos, ...parcial };
    onDatosChange(parcial);
    agendar(nuevosDatos);
  }

  function cambiarPrecioAcordado(valor: string) {
    editadoManualmente.current = true;
    onPrecioAcordadoChange?.(valor, true);
  }

  return (
    <section aria-label="Datos para cotizar" className="flex flex-col gap-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <Campo
          etiqueta="Tipo de vehículo"
          error={errores.id_tipo_vehiculo}
          id="tipo-vehiculo-cotizacion"
        >
          <select
            id="tipo-vehiculo-cotizacion"
            aria-invalid={Boolean(errores.id_tipo_vehiculo)}
            aria-describedby={
              errores.id_tipo_vehiculo ? "tipo-vehiculo-cotizacion-error" : undefined
            }
            value={datos.id_tipo_vehiculo}
            onChange={(evento) => cambiar({ id_tipo_vehiculo: evento.target.value })}
            className={claseControl}
          >
            <option value="">Elegí un tipo de vehículo</option>
            {tiposVehiculo.map((tipo) => (
              <option key={tipo.id} value={tipo.id}>
                {tipo.descripcion}
              </option>
            ))}
          </select>
        </Campo>

        <Campo
          etiqueta="Horas estimadas"
          error={errores.horas_estimadas}
          id="horas-cotizacion"
        >
          <input
            id="horas-cotizacion"
            type="number"
            min="1"
            step="0.01"
            inputMode="decimal"
            aria-invalid={Boolean(errores.horas_estimadas)}
            aria-describedby={
              errores.horas_estimadas ? "horas-cotizacion-error" : undefined
            }
            value={datos.horas_estimadas}
            onChange={(evento) => cambiar({ horas_estimadas: evento.target.value })}
            className={claseControl}
          />
        </Campo>

        <Campo
          etiqueta="Kilómetros estimados"
          error={errores.km_estimados}
          id="km-cotizacion"
        >
          <input
            id="km-cotizacion"
            type="number"
            min="0"
            step="0.01"
            inputMode="decimal"
            aria-invalid={Boolean(errores.km_estimados)}
            aria-describedby={errores.km_estimados ? "km-cotizacion-error" : undefined}
            value={datos.km_estimados}
            onChange={(evento) => cambiar({ km_estimados: evento.target.value })}
            className={claseControl}
          />
        </Campo>

        <fieldset className="grid gap-2 rounded-lg border border-panel-borde/70 bg-panel-suave/30 p-3 sm:col-span-2 sm:grid-cols-2">
          <legend className="px-1 text-sm font-medium text-panel-texto">
            Condiciones del viaje
          </legend>
          <OpcionCheck
            etiqueta="Requiere ayudante"
            marcada={Boolean(datos.requiere_ayudante)}
            alCambiar={(marcada) => cambiar({ requiere_ayudante: marcada })}
          />
          <OpcionCheck
            etiqueta="Acceso con escalera"
            marcada={Boolean(datos.acceso_escalera)}
            alCambiar={(marcada) => cambiar({ acceso_escalera: marcada })}
          />
          <OpcionCheck
            etiqueta="Zona concurrida"
            marcada={Boolean(datos.zona_concurrida)}
            alCambiar={(marcada) => cambiar({ zona_concurrida: marcada })}
          />
          <OpcionCheck
            etiqueta="Urgencia para el mismo día"
            marcada={Boolean(datos.urgencia_mismo_dia)}
            alCambiar={(marcada) => cambiar({ urgencia_mismo_dia: marcada })}
          />
        </fieldset>
      </div>

      <p aria-live="polite" className="text-sm text-panel-secundario">
        {calculando
          ? "Calculando el precio sugerido…"
          : !datos.id_tipo_vehiculo
            ? "Elegí un tipo de vehículo para consultar las tarifas."
            : !cotizacion && !mensaje
              ? "El precio sugerido se actualiza al cambiar los datos."
              : null}
      </p>

      {mensaje ? (
        <p
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 dark:border-[#7f1d1d] dark:bg-[#3b1416] dark:text-red-300"
        >
          {mensaje}
          {incluirPrecioAcordado
            ? " Podés registrar el servicio con un precio acordado válido; el servidor volverá a calcular el sugerido."
            : null}
        </p>
      ) : null}

      {cotizacion ? <ResumenCotizacion cotizacion={cotizacion} /> : null}

      {incluirPrecioAcordado ? (
        <Campo
          etiqueta="Precio final acordado"
          error={errores.precio_acordado}
          id="precio_acordado"
        >
          <input
            id="precio_acordado"
            aria-label="Precio final acordado"
            aria-invalid={Boolean(errores.precio_acordado)}
            aria-describedby={
              errores.precio_acordado ? "precio_acordado-error" : undefined
            }
            type="number"
            min="0"
            step="0.01"
            inputMode="decimal"
            value={precioAcordado}
            onChange={(evento) => cambiarPrecioAcordado(evento.target.value)}
            className={claseControl}
          />
          {!errores.precio_acordado ? (
            <span className="text-xs font-normal text-panel-secundario">
              Se completa con el sugerido hasta que lo edites.
            </span>
          ) : null}
        </Campo>
      ) : null}
    </section>
  );
}

function Campo({
  id,
  etiqueta,
  error,
  children,
}: {
  id: string;
  etiqueta: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-medium text-panel-texto">
        {etiqueta}
      </label>
      {children}
      {error ? (
        <span id={`${id}-error`} className="text-xs text-alerta">
          {error}
        </span>
      ) : null}
    </div>
  );
}

function OpcionCheck({
  etiqueta,
  marcada,
  alCambiar,
}: {
  etiqueta: string;
  marcada: boolean;
  alCambiar: (marcada: boolean) => void;
}) {
  return (
    <label className="flex min-h-9 items-center gap-2 rounded-md px-2 text-sm text-panel-texto">
      <input
        type="checkbox"
        checked={marcada}
        onChange={(evento) => alCambiar(evento.target.checked)}
        className="size-4 accent-panel-azul focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul"
      />
      {etiqueta}
    </label>
  );
}

const claseControl =
  "block min-h-10 w-full rounded-lg border border-panel-borde/80 bg-white px-3 py-2 text-sm text-panel-texto shadow-xs transition-colors focus:border-panel-azul focus:ring-2 focus:ring-panel-azul/20 focus-visible:outline-none dark:bg-[#0d1626] dark:text-white";
