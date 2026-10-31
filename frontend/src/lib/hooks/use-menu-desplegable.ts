"use client";

import { useCallback, useEffect, useRef, useState, type CSSProperties } from "react";

const MARGEN = 8;
const ANCHO_POR_DEFECTO = 272;
const ALTO_ESTIMADO = 280;

type Posicion = { top: number; left: number; width: number };

/**
 * Estado de un menú de acciones anclado a un botón `...`.
 *
 * El menú se posiciona con `position: fixed` para que no lo recorte el
 * `overflow-hidden` de la tarjeta ni el `overflow-x-auto` de la tabla. Se cierra
 * al hacer clic afuera y con `Escape`; `cerrar()` permite cerrarlo desde la fila
 * cuando se abre un modal.
 */
export function useMenuDesplegable(ancho = ANCHO_POR_DEFECTO) {
  const [abierto, setAbierto] = useState(false);
  const [posicion, setPosicion] = useState<Posicion | null>(null);
  const anclaRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const calcular = useCallback((): Posicion | null => {
    const ancla = anclaRef.current;
    if (!ancla || typeof window === "undefined") {
      return null;
    }

    const rect = ancla.getBoundingClientRect();
    const anchoDisponible = Math.min(ancho, window.innerWidth - MARGEN * 2);
    const left = Math.min(
      Math.max(rect.right - anchoDisponible, MARGEN),
      window.innerWidth - anchoDisponible - MARGEN,
    );
    const alto = menuRef.current?.offsetHeight ?? ALTO_ESTIMADO;
    const abreHaciaArriba =
      rect.bottom + MARGEN + alto > window.innerHeight && rect.top > alto + MARGEN;
    const top = abreHaciaArriba ? rect.top - MARGEN - alto : rect.bottom + MARGEN;

    return { top: Math.max(MARGEN, top), left, width: anchoDisponible };
  }, [ancho]);

  const abrir = useCallback(() => {
    setPosicion(calcular());
    setAbierto(true);
  }, [calcular]);

  const cerrar = useCallback(() => {
    setAbierto(false);
    setPosicion(null);
  }, []);

  const alternar = useCallback(() => {
    if (abierto) {
      cerrar();
      return;
    }
    abrir();
  }, [abierto, abrir, cerrar]);

  useEffect(() => {
    if (!abierto) {
      return;
    }

    const reposicionar = () => setPosicion(calcular());
    window.addEventListener("scroll", reposicionar, true);
    window.addEventListener("resize", reposicionar);
    return () => {
      window.removeEventListener("scroll", reposicionar, true);
      window.removeEventListener("resize", reposicionar);
    };
  }, [abierto, calcular]);

  useEffect(() => {
    if (!abierto) {
      return;
    }

    function alSenalar(evento: PointerEvent) {
      const objetivo = evento.target;
      if (!(objetivo instanceof Node)) {
        return;
      }
      if (menuRef.current?.contains(objetivo) || anclaRef.current?.contains(objetivo)) {
        return;
      }
      cerrar();
    }

    function alTeclear(evento: KeyboardEvent) {
      if (evento.key !== "Escape") {
        return;
      }
      cerrar();
      anclaRef.current?.querySelector<HTMLElement>("button")?.focus();
    }

    document.addEventListener("pointerdown", alSenalar);
    document.addEventListener("keydown", alTeclear);
    return () => {
      document.removeEventListener("pointerdown", alSenalar);
      document.removeEventListener("keydown", alTeclear);
    };
  }, [abierto, cerrar]);

  const estilo: CSSProperties | undefined = posicion
    ? {
        position: "fixed",
        top: posicion.top,
        left: posicion.left,
        width: posicion.width,
      }
    : undefined;

  return { abierto, abrir, cerrar, alternar, anclaRef, menuRef, estilo };
}
