"use client";

import { useEffect, useRef, useState } from "react";

import { buscarDireccionesMapa } from "@/features/servicios/actions";
import type { DireccionOpcion } from "@/features/servicios/types";

type Propiedades = {
  id: string;
  etiqueta: string;
  seleccion: DireccionOpcion | null;
  onSeleccionar: (opcion: DireccionOpcion | null) => void;
};

export function CampoDireccionMapa({
  id,
  etiqueta,
  seleccion,
  onSeleccionar,
}: Propiedades) {
  const [consulta, setConsulta] = useState("");
  const [opciones, setOpciones] = useState<DireccionOpcion[]>([]);
  const [estaBuscando, setEstaBuscando] = useState(false);
  const [error, setError] = useState("");
  const solicitud = useRef(0);
  const idLista = `${id}-opciones`;

  useEffect(
    () => () => {
      solicitud.current += 1;
    },
    [],
  );

  function cambiarConsulta(valor: string) {
    setConsulta(valor);
    setOpciones([]);
    setError("");
    setEstaBuscando(false);
    onSeleccionar(null);
    solicitud.current += 1;
  }

  async function buscar() {
    const consultaLimpia = consulta.trim();
    if (consultaLimpia.length < 3 || estaBuscando || seleccion) {
      return;
    }

    setOpciones([]);
    setError("");
    setEstaBuscando(true);
    solicitud.current += 1;
    const idSolicitud = solicitud.current;

    try {
      const respuesta = await buscarDireccionesMapa(consultaLimpia);
      if (solicitud.current !== idSolicitud) {
        return;
      }
      if (!respuesta.ok) {
        setError(respuesta.mensaje);
        return;
      }
      setOpciones(respuesta.dato);
      if (respuesta.dato.length === 0) {
        setError("No encontramos direcciones para esa búsqueda.");
      }
    } catch {
      if (solicitud.current === idSolicitud) {
        setError("No pudimos buscar la dirección. Intentá de nuevo.");
      }
    } finally {
      if (solicitud.current === idSolicitud) {
        setEstaBuscando(false);
      }
    }
  }

  function seleccionar(opcion: DireccionOpcion) {
    solicitud.current += 1;
    setConsulta(opcion.etiqueta);
    setOpciones([]);
    setError("");
    setEstaBuscando(false);
    onSeleccionar(opcion);
  }

  return (
    <div className="relative min-w-0">
      <label htmlFor={id} className="block text-xs font-semibold text-panel-secundario">
        {etiqueta}
      </label>
      <div className="mt-1 flex gap-2">
        <input
          id={id}
          type="search"
          autoComplete="off"
          aria-describedby={error ? `${id}-error` : `${id}-ayuda`}
          value={seleccion?.etiqueta ?? consulta}
          onChange={(evento) => cambiarConsulta(evento.target.value)}
          onKeyDown={(evento) => {
            if (evento.key === "Enter") {
              evento.preventDefault();
              void buscar();
            }
          }}
          className="block min-h-10 min-w-0 flex-1 rounded-lg border border-panel-borde/80 bg-white px-3 py-2 text-sm text-panel-texto shadow-xs transition-colors focus:border-panel-azul focus:ring-2 focus:ring-panel-azul/20 focus-visible:outline-none dark:bg-[#0d1626] dark:text-white"
        />
        <button
          type="button"
          onClick={() => void buscar()}
          disabled={consulta.trim().length < 3 || estaBuscando || Boolean(seleccion)}
          className="inline-flex min-h-10 shrink-0 items-center gap-2 rounded-lg border border-panel-borde bg-panel-superficie px-3 text-xs font-semibold text-panel-texto transition-colors hover:bg-panel-suave disabled:cursor-not-allowed disabled:opacity-50"
        >
          {estaBuscando ? (
            <span
              role="status"
              aria-label={`Buscando ${etiqueta.toLowerCase()}`}
              className="size-4 animate-spin rounded-full border-2 border-panel-borde border-t-panel-primario motion-reduce:animate-none"
            />
          ) : null}
          {estaBuscando ? "Buscando…" : `Buscar ${etiqueta}`}
        </button>
      </div>
      <p id={`${id}-ayuda`} className="mt-1 text-[11px] text-panel-secundario">
        Escribí al menos 3 caracteres y presioná Buscar.
      </p>
      {opciones.length > 0 ? (
        <ul
          id={idLista}
          role="listbox"
          aria-label={`Sugerencias para ${etiqueta.toLowerCase()}`}
          className="absolute z-20 mt-1 max-h-52 w-full overflow-y-auto rounded-lg border border-panel-borde bg-panel-superficie py-1 shadow-lg"
        >
          {opciones.map((opcion) => (
            <li key={`${opcion.etiqueta}-${opcion.longitud}-${opcion.latitud}`}>
              <button
                type="button"
                role="option"
                aria-selected={false}
                onClick={() => seleccionar(opcion)}
                className="w-full px-3 py-2 text-left text-sm text-panel-texto hover:bg-panel-suave focus-visible:bg-panel-suave focus-visible:outline-none"
              >
                {opcion.etiqueta}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      {error ? (
        <p id={`${id}-error`} role="alert" className="mt-1 text-xs text-alerta">
          {error}
        </p>
      ) : null}
    </div>
  );
}
