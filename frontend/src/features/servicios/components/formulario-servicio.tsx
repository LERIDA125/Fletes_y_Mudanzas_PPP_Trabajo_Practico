"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useForm, useWatch } from "react-hook-form";

import {
  consultarDisponibilidadServicio,
  obtenerCatalogosServicio,
  registrarServicio,
} from "@/features/servicios/actions";
import type {
  ClienteOpcion,
  Disponibilidad,
  TipoVehiculoOpcion,
} from "@/features/servicios/types";
import type { DatosCotizacion } from "@/features/cotizaciones/schemas/cotizacion";
import { FormularioCotizacion } from "@/features/cotizaciones/components/formulario-cotizacion";
import {
  esquemaFormularioServicio,
  type EntradaFormularioServicio,
  type ValoresFormularioServicio,
} from "@/features/servicios/schemas/servicio";

const formatoMoneda = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
});

type Propiedades = {
  // Si no se pasan, el formulario los pide al abrirse. Así la página puede
  // renderizar el botón de alta sin esperar a la API.
  clientes?: ClienteOpcion[];
  tiposVehiculo?: TipoVehiculoOpcion[];
  abrirInicial?: boolean;
};

const VALORES_INICIALES: ValoresFormularioServicio = {
  modo_cliente: "existente",
  id_cliente: "",
  razon_social: "",
  telefono: "",
  direccion_habitual: "",
  tiene_cuenta_corriente: false,
  id_tipo_vehiculo: "",
  fecha: "", // Se completa con la fecha local al abrir el modal (evita `new Date()` en el prerender).
  hora_inicio: "",
  horas_estimadas: "1",
  km_estimados: "0",
  requiere_ayudante: false,
  acceso_escalera: false,
  zona_concurrida: false,
  urgencia_mismo_dia: false,
  precio_acordado: "",
  id_chofer: "",
  id_vehiculo: "",
};

function valoresIniciales(): ValoresFormularioServicio {
  return { ...VALORES_INICIALES };
}

function fechaLocal(): string {
  const fecha = new Date();
  const anio = fecha.getFullYear();
  const mes = String(fecha.getMonth() + 1).padStart(2, "0");
  const dia = String(fecha.getDate()).padStart(2, "0");
  return `${anio}-${mes}-${dia}`;
}

const TIEMPO_DE_ESPERA_MS = 350;

export function FormularioServicio({
  clientes: clientesIniciales,
  tiposVehiculo: tiposVehiculoIniciales,
  abrirInicial = false,
}: Propiedades) {
  const router = useRouter();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const aperturaAplicada = useRef(false);
  const solicitudDisponibilidad = useRef(0);
  const cargaDeCatalogosEnCurso = useRef(false);
  const debeCargarAlAbrir =
    clientesIniciales === undefined || tiposVehiculoIniciales === undefined;
  const [clientes, setClientes] = useState<ClienteOpcion[]>(clientesIniciales ?? []);
  const [tiposVehiculo, setTiposVehiculo] = useState<TipoVehiculoOpcion[]>(
    tiposVehiculoIniciales ?? [],
  );
  const [catalogosCargados, setCatalogosCargados] = useState(!debeCargarAlAbrir);
  const [cargandoCatalogos, setCargandoCatalogos] = useState(false);
  const [errorCatalogos, setErrorCatalogos] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [servicioCreado, setServicioCreado] = useState<string | null>(null);
  const [estaRegistrando, setEstaRegistrando] = useState(false);
  const [reinicioCotizador, setReinicioCotizador] = useState(0);
  const [disponibilidad, setDisponibilidad] = useState<Disponibilidad | null>(null);
  const [cargandoDisponibilidad, setCargandoDisponibilidad] = useState(false);
  const [errorDisponibilidad, setErrorDisponibilidad] = useState("");

  const {
    register,
    control,
    getValues,
    setValue,
    handleSubmit,
    reset,
    clearErrors,
    formState: { errors },
  } = useForm<EntradaFormularioServicio, unknown, ValoresFormularioServicio>({
    resolver: zodResolver(esquemaFormularioServicio),
    defaultValues: valoresIniciales(),
  });

  const valores = useWatch({ control });
  const clienteNuevo = valores.modo_cliente === "nuevo";
  const catalogosDisponibles =
    tiposVehiculo.length > 0 && (clienteNuevo || clientes.length > 0);
  const datosCotizacion: DatosCotizacion = {
    id_tipo_vehiculo: valores.id_tipo_vehiculo ?? "",
    horas_estimadas: valores.horas_estimadas ?? "1",
    km_estimados: valores.km_estimados ?? "0",
    requiere_ayudante: valores.requiere_ayudante ?? false,
    acceso_escalera: valores.acceso_escalera ?? false,
    zona_concurrida: valores.zona_concurrida ?? false,
    urgencia_mismo_dia: valores.urgencia_mismo_dia ?? false,
  };

  // Los catálogos se piden recién al abrir el modal. Si fallan, el formulario
  // sigue visible y muestra el error; al reabrir se vuelve a intentar.
  const cargarCatalogos = useCallback(async () => {
    if (catalogosCargados || cargaDeCatalogosEnCurso.current) {
      return;
    }
    cargaDeCatalogosEnCurso.current = true;
    setCargandoCatalogos(true);
    setErrorCatalogos("");
    try {
      const respuesta = await obtenerCatalogosServicio();
      if (!respuesta.ok) {
        setErrorCatalogos(respuesta.mensaje);
        return;
      }
      setClientes(respuesta.dato.clientes);
      setTiposVehiculo(respuesta.dato.tiposVehiculo);
      setCatalogosCargados(true);
    } catch {
      setErrorCatalogos(
        "No pudimos cargar clientes y tipos de vehículo. Cerrá y volvé a abrir el formulario.",
      );
    } finally {
      cargaDeCatalogosEnCurso.current = false;
      setCargandoCatalogos(false);
    }
  }, [catalogosCargados]);

  useEffect(() => {
    if (!abrirInicial || aperturaAplicada.current) {
      return;
    }
    aperturaAplicada.current = true;
    if (!getValues("fecha")) {
      setValue("fecha", fechaLocal());
    }
    dialogRef.current?.showModal();
    void cargarCatalogos();
  }, [abrirInicial, cargarCatalogos, getValues, setValue]);

  useEffect(() => {
    const idTipo = Number(valores.id_tipo_vehiculo);
    const horasSanitizadas = String(valores.horas_estimadas ?? "").replace(",", ".");
    const horas = Number(horasSanitizadas);
    const fecha = valores.fecha;
    let horaInicioSanitizada: string | null = valores.hora_inicio || null;
    if (horaInicioSanitizada === "") {
      horaInicioSanitizada = null;
    } else if (horaInicioSanitizada && horaInicioSanitizada.length === 5) {
      horaInicioSanitizada = `${horaInicioSanitizada}:00`;
    }
    const horaInicio = horaInicioSanitizada;
    const idSolicitud = solicitudDisponibilidad.current + 1;
    solicitudDisponibilidad.current = idSolicitud;

    // Todo el trabajo (incluidos los setState) ocurre dentro del temporizador:
    // así el efecto no dispara renders en cascada y el debounce sigue vigente.
    const temporizador = setTimeout(async () => {
      if (!fecha || !idTipo || !Number.isFinite(horas) || horas < 1) {
        setDisponibilidad(null);
        setErrorDisponibilidad("");
        setCargandoDisponibilidad(false);
        return;
      }

      setCargandoDisponibilidad(true);
      try {
        const respuesta = await consultarDisponibilidadServicio({
          fecha,
          id_tipo_vehiculo: idTipo,
          horas_estimadas: horas,
          hora_inicio: horaInicio,
        });
        if (solicitudDisponibilidad.current !== idSolicitud) {
          return;
        }
        setCargandoDisponibilidad(false);
        if (respuesta.ok) {
          setDisponibilidad(respuesta.dato);
          setErrorDisponibilidad("");
          return;
        }
        setDisponibilidad(null);
        setErrorDisponibilidad(respuesta.mensaje);
      } catch {
        if (solicitudDisponibilidad.current !== idSolicitud) {
          return;
        }
        setCargandoDisponibilidad(false);
        setDisponibilidad(null);
        setErrorDisponibilidad("No pudimos consultar la disponibilidad.");
      }
    }, TIEMPO_DE_ESPERA_MS);

    return () => clearTimeout(temporizador);
  }, [
    valores.fecha,
    valores.id_tipo_vehiculo,
    valores.horas_estimadas,
    valores.hora_inicio,
  ]);

  const tipoSeleccionado = Number(valores.id_tipo_vehiculo);
  const vehiculosDisponibles = useMemo(() => {
    if (!disponibilidad || disponibilidad.id_tipo_vehiculo !== tipoSeleccionado) {
      return [];
    }
    return disponibilidad.vehiculos.filter(
      (vehiculo) => vehiculo.id_tipo_vehiculo === tipoSeleccionado,
    );
  }, [disponibilidad, tipoSeleccionado]);

  useEffect(() => {
    if (!disponibilidad) {
      return;
    }
    const choferElegido = getValues("id_chofer");
    if (
      choferElegido &&
      !disponibilidad.choferes.some((chofer) => String(chofer.id) === choferElegido)
    ) {
      setValue("id_chofer", "");
    }
    const vehiculoElegido = getValues("id_vehiculo");
    if (
      vehiculoElegido &&
      !vehiculosDisponibles.some((vehiculo) => String(vehiculo.id) === vehiculoElegido)
    ) {
      setValue("id_vehiculo", "");
    }
  }, [disponibilidad, getValues, setValue, vehiculosDisponibles]);

  async function confirmarYCrear(actual: ValoresFormularioServicio) {
    setMensaje("");
    setEstaRegistrando(true);
    try {
      const asignaciones = {
        ...(actual.id_chofer ? { id_chofer: Number(actual.id_chofer) } : {}),
        ...(actual.id_vehiculo ? { id_vehiculo: Number(actual.id_vehiculo) } : {}),
      };
      const cliente =
        actual.modo_cliente === "nuevo"
          ? {
              nuevo_cliente: {
                razon_social: actual.razon_social.trim(),
                telefono: actual.telefono.trim(),
                direccion_habitual: actual.direccion_habitual.trim(),
                tiene_cuenta_corriente: actual.tiene_cuenta_corriente ?? false,
              },
            }
          : { id_cliente: Number(actual.id_cliente) };

      const respuesta = await registrarServicio({
        ...cliente,
        ...asignaciones,
        id_tipo_vehiculo: Number(actual.id_tipo_vehiculo),
        fecha: actual.fecha,
        hora_inicio: actual.hora_inicio || null,
        horas_estimadas: Number(actual.horas_estimadas),
        km_estimados: Number(actual.km_estimados),
        requiere_ayudante: actual.requiere_ayudante,
        acceso_escalera: actual.acceso_escalera,
        zona_concurrida: actual.zona_concurrida,
        urgencia_mismo_dia: actual.urgencia_mismo_dia,
        precio_acordado: Number(actual.precio_acordado),
      });
      if (!respuesta.ok) {
        setMensaje(respuesta.mensaje);
        return;
      }

      setServicioCreado(
        `Servicio #${respuesta.dato.id_servicio} registrado. Precio acordado: ${formatoMoneda.format(
          Number(respuesta.dato.precio_acordado),
        )}.`,
      );
      setDisponibilidad(null);
      reset({ ...valoresIniciales(), fecha: fechaLocal() });
      setReinicioCotizador((actualReinicio) => actualReinicio + 1);
      router.refresh();
    } finally {
      setEstaRegistrando(false);
    }
  }

  function cambiarModoCliente(modo: "existente" | "nuevo") {
    clearErrors(["id_cliente", "razon_social", "telefono", "direccion_habitual"]);
    setValue("modo_cliente", modo);
  }

  function cambiarDatosCotizacion(parcial: Partial<DatosCotizacion>) {
    if (parcial.id_tipo_vehiculo !== undefined) {
      const cambioTipo = parcial.id_tipo_vehiculo !== getValues("id_tipo_vehiculo");
      setValue("id_tipo_vehiculo", parcial.id_tipo_vehiculo, {
        shouldDirty: true,
        shouldValidate: true,
      });
      if (cambioTipo && getValues("id_vehiculo")) {
        setValue("id_vehiculo", "", { shouldDirty: true });
      }
    }
    if (parcial.horas_estimadas !== undefined) {
      setValue("horas_estimadas", parcial.horas_estimadas, { shouldDirty: true });
    }
    if (parcial.km_estimados !== undefined) {
      setValue("km_estimados", parcial.km_estimados, { shouldDirty: true });
    }
    if (parcial.requiere_ayudante !== undefined) {
      setValue("requiere_ayudante", parcial.requiere_ayudante, {
        shouldDirty: true,
      });
    }
    if (parcial.acceso_escalera !== undefined) {
      setValue("acceso_escalera", parcial.acceso_escalera, { shouldDirty: true });
    }
    if (parcial.zona_concurrida !== undefined) {
      setValue("zona_concurrida", parcial.zona_concurrida, { shouldDirty: true });
    }
    if (parcial.urgencia_mismo_dia !== undefined) {
      setValue("urgencia_mismo_dia", parcial.urgencia_mismo_dia, {
        shouldDirty: true,
      });
    }
  }

  function cambiarPrecioAcordado(valor: string, manual: boolean) {
    setValue("precio_acordado", valor, {
      shouldDirty: manual,
      shouldValidate: true,
    });
  }

  function abrirFormulario() {
    if (!getValues("fecha")) {
      setValue("fecha", fechaLocal());
    }
    dialogRef.current?.showModal();
    void cargarCatalogos();
  }

  return (
    <>
      <button
        type="button"
        onClick={abrirFormulario}
        className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-orange-200 transition-all hover:bg-orange-600 active:scale-[0.99] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500"
      >
        <span className="text-base font-bold leading-none" aria-hidden="true">
          +
        </span>
        <span>Nuevo servicio</span>
        <span className="hidden sm:inline"> / Cotizar</span>
      </button>

      <dialog
        ref={dialogRef}
        aria-labelledby="titulo-formulario-servicio"
        className="m-auto max-h-[92dvh] w-[calc(100%-2rem)] max-w-2xl overflow-y-auto rounded-xl border border-panel-borde/70 bg-panel-superficie p-0 text-panel-texto shadow-2xl backdrop:bg-slate-950/60 backdrop:backdrop-blur-sm"
      >
        <div className="flex items-start justify-between gap-4 border-b border-panel-borde/60 bg-panel-suave/40 px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-panel-primario text-white shadow-sm">
              <svg
                className="size-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <div>
              <h2
                id="titulo-formulario-servicio"
                className="text-lg font-bold text-panel-texto"
              >
                Cotizar y registrar un servicio
              </h2>
              <p className="mt-0.5 text-xs text-panel-secundario">
                La cotización oficial se calcula en el servidor con tarifas vigentes.
              </p>
            </div>
          </div>
          <button
            type="button"
            aria-label="Cerrar formulario"
            onClick={() => dialogRef.current?.close()}
            className="inline-flex size-8 shrink-0 items-center justify-center rounded-lg text-panel-secundario transition-colors hover:bg-panel-suave hover:text-panel-texto focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul"
          >
            <svg
              aria-hidden="true"
              className="size-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path strokeLinecap="round" d="m6 6 12 12M18 6 6 18" />
            </svg>
          </button>
        </div>

        <form
          className="grid gap-4 p-6 sm:grid-cols-2"
          noValidate
          onSubmit={handleSubmit(confirmarYCrear)}
        >
          <div className="sm:col-span-2 rounded-lg bg-blue-50/80 border border-blue-100 p-3 text-xs text-blue-900 leading-relaxed dark:bg-[#12233d] dark:border-[#1e3a5f] dark:text-[#bfdbfe]">
            Completá los datos del viaje para obtener el importe tarifado oficial. Luego
            podrás confirmar el alta definitiva.
          </div>

          {cargandoCatalogos ? (
            <p role="status" className="sm:col-span-2 text-xs text-panel-secundario">
              Cargando clientes y tipos de vehículo…
            </p>
          ) : null}

          {errorCatalogos ? (
            <p
              role="alert"
              className="sm:col-span-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 dark:border-[#7f1d1d] dark:bg-[#3b1416] dark:text-red-300"
            >
              {errorCatalogos}
            </p>
          ) : null}

          <fieldset className="sm:col-span-2">
            <legend className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario">
              Cliente
            </legend>
            <div className="mt-2 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => cambiarModoCliente("existente")}
                aria-pressed={!clienteNuevo}
                disabled={clientes.length === 0}
                className={botonModo(!clienteNuevo)}
              >
                Cliente existente
              </button>
              <button
                type="button"
                onClick={() => cambiarModoCliente("nuevo")}
                aria-pressed={clienteNuevo}
                className={botonModo(clienteNuevo)}
              >
                Cliente nuevo
              </button>
            </div>
          </fieldset>

          {clienteNuevo ? (
            <>
              <p className="sm:col-span-2 text-xs text-panel-secundario">
                El sistema crea el cliente y lo vincula al servicio. Si ya existe uno con
                la misma razón social, reutiliza ese registro.
              </p>
              <Campo
                id="razon_social"
                etiqueta="Razón social"
                error={errors.razon_social?.message}
              >
                <input
                  id="razon_social"
                  aria-invalid={Boolean(errors.razon_social)}
                  aria-describedby={
                    errors.razon_social ? "razon_social-error" : undefined
                  }
                  {...register("razon_social")}
                  className={claseControl}
                />
              </Campo>
              <Campo id="telefono" etiqueta="Teléfono" error={errors.telefono?.message}>
                <input
                  id="telefono"
                  type="tel"
                  inputMode="tel"
                  aria-invalid={Boolean(errors.telefono)}
                  aria-describedby={errors.telefono ? "telefono-error" : undefined}
                  {...register("telefono")}
                  className={claseControl}
                />
              </Campo>
              <Campo
                id="direccion_habitual"
                etiqueta="Dirección habitual"
                error={errors.direccion_habitual?.message}
              >
                <input
                  id="direccion_habitual"
                  aria-invalid={Boolean(errors.direccion_habitual)}
                  aria-describedby={
                    errors.direccion_habitual ? "direccion_habitual-error" : undefined
                  }
                  {...register("direccion_habitual")}
                  className={claseControl}
                />
              </Campo>
              <label className="flex items-end gap-2 pb-2 text-xs font-semibold text-panel-secundario">
                <input
                  type="checkbox"
                  className="size-4 accent-panel-azul"
                  {...register("tiene_cuenta_corriente")}
                />
                <span>Tiene cuenta corriente</span>
              </label>
            </>
          ) : clientes.length === 0 ? (
            catalogosCargados ? (
              <p role="status" className="text-sm text-panel-secundario sm:col-span-2">
                No hay clientes activos para seleccionar. Podés cargar uno nuevo.
              </p>
            ) : null
          ) : (
            <Campo id="id_cliente" etiqueta="Cliente" error={errors.id_cliente?.message}>
              <select
                id="id_cliente"
                aria-invalid={Boolean(errors.id_cliente)}
                aria-describedby={errors.id_cliente ? "id_cliente-error" : undefined}
                {...register("id_cliente")}
                className={claseControl}
              >
                <option value="">Elegí un cliente</option>
                {clientes.map((cliente) => (
                  <option key={cliente.id} value={cliente.id}>
                    {cliente.razon_social}
                  </option>
                ))}
              </select>
            </Campo>
          )}

          {tiposVehiculo.length === 0 ? (
            catalogosCargados ? (
              <p role="status" className="text-sm text-panel-secundario sm:col-span-2">
                No hay tipos de vehículo activos para cotizar.
              </p>
            ) : null
          ) : (
            <>
              <input type="hidden" {...register("id_tipo_vehiculo")} />
              <div className="sm:col-span-2">
                <FormularioCotizacion
                  key={reinicioCotizador}
                  tiposVehiculo={tiposVehiculo}
                  datos={datosCotizacion}
                  onDatosChange={cambiarDatosCotizacion}
                  precioAcordado={valores.precio_acordado ?? ""}
                  onPrecioAcordadoChange={cambiarPrecioAcordado}
                  errores={{
                    id_tipo_vehiculo: errors.id_tipo_vehiculo?.message,
                    horas_estimadas: errors.horas_estimadas?.message,
                    km_estimados: errors.km_estimados?.message,
                    precio_acordado: errors.precio_acordado?.message,
                  }}
                />
              </div>
            </>
          )}

          <Campo id="fecha" etiqueta="Fecha" error={errors.fecha?.message}>
            <input
              id="fecha"
              type="date"
              aria-invalid={Boolean(errors.fecha)}
              aria-describedby={errors.fecha ? "fecha-error" : undefined}
              {...register("fecha")}
              className={claseControl}
            />
          </Campo>

          <Campo id="hora_inicio" etiqueta="Hora de inicio (opcional)">
            <input
              id="hora_inicio"
              type="time"
              {...register("hora_inicio")}
              className={claseControl}
            />
          </Campo>

          <fieldset className="sm:col-span-2 rounded-xl border border-panel-borde/70 bg-panel-suave/30 p-3">
            <legend className="px-1 text-xs font-semibold uppercase tracking-wider text-panel-secundario">
              Asignación operativa (opcional)
            </legend>
            <p className="text-[11px] text-panel-secundario">
              Solo se muestran choferes y vehículos libres en la fecha y el horario
              elegidos.
            </p>

            {errorDisponibilidad ? (
              <p role="alert" className="mt-2 text-xs font-medium text-alerta">
                {errorDisponibilidad}
              </p>
            ) : null}

            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <Campo id="id_chofer" etiqueta="Chofer">
                <select
                  id="id_chofer"
                  disabled={cargandoDisponibilidad || !disponibilidad}
                  {...register("id_chofer")}
                  className={claseControl}
                >
                  <option value="">Sin asignar</option>
                  {disponibilidad?.choferes.map((chofer) => (
                    <option key={chofer.id} value={chofer.id}>
                      {chofer.nombre_completo}
                    </option>
                  ))}
                </select>
              </Campo>

              <Campo id="id_vehiculo" etiqueta="Unidad asignada">
                <select
                  id="id_vehiculo"
                  disabled={cargandoDisponibilidad || !disponibilidad}
                  {...register("id_vehiculo")}
                  className={claseControl}
                >
                  <option value="">Sin asignar</option>
                  {vehiculosDisponibles.map((vehiculo) => (
                    <option key={vehiculo.id} value={vehiculo.id}>
                      {vehiculo.patente}
                    </option>
                  ))}
                </select>
              </Campo>
            </div>

            <p aria-live="polite" className="mt-2 text-[11px] text-panel-secundario">
              {cargandoDisponibilidad
                ? "Consultando disponibilidad…"
                : disponibilidad
                  ? `${disponibilidad.choferes.length} choferes y ${vehiculosDisponibles.length} unidades disponibles para el tipo seleccionado.`
                  : "Elegí fecha, tipo de vehículo y horas para ver la disponibilidad."}
            </p>
          </fieldset>

          {mensaje ? (
            <p
              role="alert"
              className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm font-medium text-red-700 sm:col-span-2 dark:bg-[#3b1416] dark:border-[#7f1d1d] dark:text-red-300"
            >
              {mensaje}
            </p>
          ) : null}

          {servicioCreado ? (
            <p
              role="status"
              className="rounded-lg bg-emerald-50 border border-emerald-200 px-3 py-2 text-sm font-medium text-emerald-800 sm:col-span-2 dark:bg-[#0f2e22] dark:border-[#14532d] dark:text-emerald-300"
            >
              {servicioCreado}
            </p>
          ) : null}

          <div className="sm:col-span-2 pt-2">
            <button
              type="submit"
              disabled={estaRegistrando || !catalogosDisponibles}
              className={`${claseBotonPrincipal} w-full`}
            >
              {estaRegistrando ? "Registrando…" : "Registrar servicio"}
            </button>
          </div>
        </form>
      </dialog>
    </>
  );
}

function botonModo(activo: boolean): string {
  return activo
    ? "inline-flex min-h-9 items-center justify-center rounded-lg bg-panel-primario px-3 text-xs font-bold text-white shadow-sm"
    : "inline-flex min-h-9 items-center justify-center rounded-lg border border-panel-borde bg-white px-3 text-xs font-semibold text-panel-texto transition-colors hover:bg-panel-suave dark:bg-[#0d1626] dark:text-white dark:hover:bg-[#16253d]";
}

const claseControl =
  "mt-1 block min-h-10 w-full rounded-lg border border-panel-borde/80 bg-white px-3 py-2 text-sm text-panel-texto shadow-xs transition-colors focus:border-panel-azul focus:ring-2 focus:ring-panel-azul/20 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-60 dark:bg-[#0d1626] dark:text-white";

const claseBotonPrincipal =
  "inline-flex min-h-11 items-center justify-center rounded-lg bg-panel-primario px-5 text-sm font-bold text-white shadow-md transition-all hover:bg-slate-800 active:scale-[0.99] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul disabled:cursor-not-allowed disabled:opacity-50";

function Campo({
  id,
  etiqueta,
  error,
  children,
}: {
  id: string;
  etiqueta: string;
  error?: string;
  children: React.ReactNode;
}) {
  const idError = `${id}-error`;
  return (
    <div>
      <label
        htmlFor={id}
        className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
      >
        {etiqueta}
      </label>
      {children}
      {error ? (
        <p id={idError} className="mt-1 text-xs text-alerta">
          {error}
        </p>
      ) : null}
    </div>
  );
}
