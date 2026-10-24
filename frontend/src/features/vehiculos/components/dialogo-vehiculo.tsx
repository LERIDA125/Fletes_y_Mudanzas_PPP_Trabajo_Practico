"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { useForm } from "react-hook-form";

import type { Chofer } from "@/features/choferes/types";
import { guardarVehiculo, obtenerCatalogosVehiculo } from "@/features/vehiculos/actions";
import {
  esquemaVehiculo,
  type ValoresVehiculo,
} from "@/features/vehiculos/schemas/vehiculo";
import type { TipoVehiculo, Vehiculo } from "@/features/vehiculos/types";

type Propiedades = {
  vehiculo?: Vehiculo;
  tiposVehiculo?: TipoVehiculo[];
  choferes?: Chofer[];
};

export function DialogoVehiculo({ vehiculo, tiposVehiculo, choferes }: Propiedades) {
  const router = useRouter();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [mensaje, setMensaje] = useState("");
  const [enviando, setEnviando] = useState(false);
  const editando = vehiculo !== undefined;

  // En el encabezado no se pasan catálogos: se piden recién al abrir el modal.
  // Así el botón se renderiza al instante aunque la API esté lenta o caída.
  const debeCargarAlAbrir = tiposVehiculo === undefined || choferes === undefined;
  const [tiposDisponibles, setTiposDisponibles] = useState<TipoVehiculo[]>(
    tiposVehiculo ?? [],
  );
  const [choferesDisponibles, setChoferesDisponibles] = useState<Chofer[]>(
    choferes ?? [],
  );
  const [catalogosCargados, setCatalogosCargados] = useState(!debeCargarAlAbrir);
  const [cargandoCatalogos, setCargandoCatalogos] = useState(false);
  const [errorCatalogos, setErrorCatalogos] = useState("");

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ValoresVehiculo>({
    resolver: zodResolver(esquemaVehiculo),
    defaultValues: {
      patente: vehiculo?.patente ?? "",
      id_tipo_vehiculo: String(vehiculo?.id_tipo_vehiculo ?? ""),
      id_chofer_habitual: String(vehiculo?.id_chofer_habitual ?? ""),
    },
  });

  async function asegurarCatalogos() {
    if (catalogosCargados || cargandoCatalogos) {
      return;
    }
    setCargandoCatalogos(true);
    setErrorCatalogos("");
    try {
      const respuesta = await obtenerCatalogosVehiculo();
      if (!respuesta.ok) {
        setErrorCatalogos(respuesta.mensaje);
        return;
      }
      setTiposDisponibles(respuesta.dato.tiposVehiculo);
      setChoferesDisponibles(respuesta.dato.choferes);
      setCatalogosCargados(true);
    } catch {
      setErrorCatalogos(
        "No pudimos cargar los catálogos. Cerrá y volvé a abrir el formulario.",
      );
    } finally {
      setCargandoCatalogos(false);
    }
  }

  function abrir() {
    setMensaje("");
    if (editando) {
      reset({
        patente: vehiculo.patente,
        id_tipo_vehiculo: String(vehiculo.id_tipo_vehiculo),
        id_chofer_habitual: String(vehiculo.id_chofer_habitual ?? ""),
      });
    }
    dialogRef.current?.showModal();
    void asegurarCatalogos();
  }

  async function guardar(valores: ValoresVehiculo) {
    setMensaje("");
    setEnviando(true);
    try {
      const respuesta = await guardarVehiculo(
        {
          patente: valores.patente,
          id_tipo_vehiculo: Number(valores.id_tipo_vehiculo),
          id_chofer_habitual: valores.id_chofer_habitual
            ? Number(valores.id_chofer_habitual)
            : null,
        },
        vehiculo?.id,
      );
      if (!respuesta.ok) {
        setMensaje(respuesta.mensaje);
        return;
      }
      dialogRef.current?.close();
      if (!editando) {
        reset({ patente: "", id_tipo_vehiculo: "", id_chofer_habitual: "" });
      }
      router.refresh();
    } finally {
      setEnviando(false);
    }
  }

  const sufijo = vehiculo?.id ?? "nuevo";
  // Mientras no se hayan pedido los catálogos el botón debe poder abrir el modal
  // para cargarlos; recién se deshabilita si la carga terminó sin tipos.
  const sinTipos = catalogosCargados && tiposDisponibles.length === 0;

  return (
    <>
      {editando ? (
        <button
          type="button"
          onClick={abrir}
          aria-label={`Editar vehículo ${vehiculo.patente}`}
          className="inline-flex min-h-8 items-center justify-center rounded-lg border border-panel-borde/70 bg-white px-2.5 text-xs font-semibold text-panel-texto transition-colors hover:bg-panel-suave/70 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white dark:hover:bg-[#16253d]"
        >
          Editar
        </button>
      ) : (
        <button
          type="button"
          onClick={abrir}
          disabled={sinTipos}
          title={sinTipos ? "Primero configurá al menos un tipo de vehículo." : undefined}
          className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-orange-200 transition-all hover:bg-orange-600 active:scale-[0.99] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span className="text-base font-bold leading-none" aria-hidden="true">
            +
          </span>
          <span>Nuevo vehículo</span>
        </button>
      )}

      <dialog
        ref={dialogRef}
        aria-labelledby={`titulo-dialogo-vehiculo-${sufijo}`}
        className="m-auto max-h-[92dvh] w-[calc(100%-2rem)] max-w-md overflow-y-auto rounded-xl border border-panel-borde/70 bg-panel-superficie p-0 text-panel-texto shadow-2xl backdrop:bg-slate-950/60 backdrop:backdrop-blur-sm"
      >
        <div className="flex items-start justify-between gap-4 border-b border-panel-borde/60 bg-panel-suave/40 px-6 py-5">
          <div>
            <h2
              id={`titulo-dialogo-vehiculo-${sufijo}`}
              className="text-lg font-bold text-panel-texto"
            >
              {editando ? "Editar vehículo" : "Nuevo vehículo"}
            </h2>
            <p className="mt-0.5 text-xs text-panel-secundario">
              {editando
                ? "Actualizá la patente, el tipo o el chofer habitual."
                : "Sumá una unidad a la flota operativa."}
            </p>
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
          className="flex flex-col gap-4 p-6"
          noValidate
          onSubmit={handleSubmit(guardar)}
        >
          {cargandoCatalogos ? (
            <p role="status" className="text-xs text-panel-secundario">
              Cargando tipos de vehículo y choferes…
            </p>
          ) : null}

          {errorCatalogos ? (
            <p
              role="alert"
              className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700"
            >
              {errorCatalogos}
            </p>
          ) : null}

          {!cargandoCatalogos && catalogosCargados && tiposDisponibles.length === 0 ? (
            <p
              role="alert"
              className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-medium text-amber-800"
            >
              No hay tipos de vehículo activos. Configurá uno antes de crear vehículos.
            </p>
          ) : null}

          <div>
            <label
              htmlFor={`patente-${sufijo}`}
              className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
            >
              Patente
            </label>
            <input
              id={`patente-${sufijo}`}
              placeholder="AA 123 ABC"
              aria-invalid={Boolean(errors.patente)}
              aria-describedby={errors.patente ? `patente-error-${sufijo}` : undefined}
              autoComplete="off"
              {...register("patente")}
              className={claseControl}
            />
            {errors.patente ? (
              <p id={`patente-error-${sufijo}`} className="mt-1 text-xs text-alerta">
                {errors.patente.message}
              </p>
            ) : null}
          </div>

          <div>
            <label
              htmlFor={`id_tipo_vehiculo-${sufijo}`}
              className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
            >
              Tipo de vehículo
            </label>
            <select
              id={`id_tipo_vehiculo-${sufijo}`}
              aria-invalid={Boolean(errors.id_tipo_vehiculo)}
              aria-describedby={
                errors.id_tipo_vehiculo ? `id_tipo_vehiculo-error-${sufijo}` : undefined
              }
              {...register("id_tipo_vehiculo")}
              className={claseControl}
            >
              <option value="">Elegí un tipo</option>
              {tiposDisponibles.map((tipo) => (
                <option key={tipo.id} value={tipo.id}>
                  {tipo.descripcion}
                </option>
              ))}
            </select>
            {errors.id_tipo_vehiculo ? (
              <p
                id={`id_tipo_vehiculo-error-${sufijo}`}
                className="mt-1 text-xs text-alerta"
              >
                {errors.id_tipo_vehiculo.message}
              </p>
            ) : null}
          </div>

          <div>
            <label
              htmlFor={`id_chofer_habitual-${sufijo}`}
              className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
            >
              Chofer habitual (opcional)
            </label>
            <select
              id={`id_chofer_habitual-${sufijo}`}
              {...register("id_chofer_habitual")}
              className={claseControl}
            >
              <option value="">Sin chofer habitual</option>
              {choferesDisponibles.map((chofer) => (
                <option key={chofer.id} value={chofer.id}>
                  {chofer.nombre_completo}
                </option>
              ))}
            </select>
          </div>

          {mensaje ? (
            <p
              role="alert"
              className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700"
            >
              {mensaje}
            </p>
          ) : null}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => dialogRef.current?.close()}
              className={claseBotonSecundario}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={enviando || cargandoCatalogos || tiposDisponibles.length === 0}
              className={claseBotonPrincipal}
            >
              {enviando ? "Guardando…" : editando ? "Guardar cambios" : "Crear vehículo"}
            </button>
          </div>
        </form>
      </dialog>
    </>
  );
}

const claseControl =
  "mt-1 block min-h-10 w-full rounded-lg border border-panel-borde/80 bg-white px-3 py-2 text-sm text-panel-texto shadow-xs transition-colors focus:border-panel-azul focus:ring-2 focus:ring-panel-azul/20 focus-visible:outline-none dark:bg-[#0d1626] dark:text-white";

const claseBotonSecundario =
  "inline-flex min-h-10 items-center justify-center rounded-lg border border-panel-borde bg-panel-suave/80 px-4 text-sm font-semibold text-panel-texto transition-all hover:bg-panel-suave focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul";

const claseBotonPrincipal =
  "inline-flex min-h-10 items-center justify-center rounded-lg bg-panel-primario px-4 text-sm font-bold text-white shadow-md transition-all hover:bg-slate-800 active:scale-[0.99] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul disabled:cursor-not-allowed disabled:opacity-50";
