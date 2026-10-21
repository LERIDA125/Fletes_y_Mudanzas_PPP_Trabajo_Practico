"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { usePathname, useRouter } from "next/navigation";

const PAUSA_DE_TECLADO_MS = 350;

type Propiedades = {
  criterioInicial: string;
};

export function BuscadorChoferes({ criterioInicial }: Propiedades) {
  const router = useRouter();
  const pathname = usePathname();
  const [texto, setTexto] = useState(criterioInicial);
  const temporizador = useRef<ReturnType<typeof setTimeout> | null>(null);

  // El único useEffect del árbol. Limpia el temporizador si el usuario se va antes de
  // que venza, y realinea el campo con la URL cuando se navega con atrás/adelante.
  // Nunca solicita datos: el criterio viaja a la URL y el Server Component hace el fetch.
  useEffect(() => {
    if (temporizador.current === null) {
      setTexto(criterioInicial);
    }
  }, [criterioInicial]);

  useEffect(() => {
    return () => {
      if (temporizador.current !== null) {
        clearTimeout(temporizador.current);
      }
    };
  }, []);

  function aplicar(termino: string) {
    // Un criterio nuevo siempre vuelve a la página 1: si no, se buscaría desde la
    // página anterior, que rara vez tiene coincidencias (FR-014).
    if (termino) {
      router.push(`${pathname}?q=${encodeURIComponent(termino)}`);
    } else {
      router.push(pathname);
    }
  }

  function alTeclear(evento: React.ChangeEvent<HTMLInputElement>) {
    const valor = evento.target.value;
    setTexto(valor);

    if (temporizador.current !== null) {
      clearTimeout(temporizador.current);
    }
    temporizador.current = setTimeout(() => {
      temporizador.current = null;
      aplicar(valor);
    }, PAUSA_DE_TECLADO_MS);
  }

  function alConfirmar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (temporizador.current !== null) {
      clearTimeout(temporizador.current);
      temporizador.current = null;
    }
    aplicar(texto.trim());
  }

  function limpiar() {
    if (temporizador.current !== null) {
      clearTimeout(temporizador.current);
      temporizador.current = null;
    }
    setTexto("");
    aplicar("");
  }

  return (
    <form role="search" onSubmit={alConfirmar} className="w-full sm:max-w-sm">
      <label htmlFor="buscador-choferes" className="sr-only">
        Buscar choferes por nombre
      </label>
      <div className="flex items-center gap-2">
        <input
          id="buscador-choferes"
          type="search"
          value={texto}
          onChange={alTeclear}
          placeholder="Buscar por nombre"
          autoComplete="off"
          className="min-w-0 flex-1 rounded-[4px] border border-papel/25 bg-papel/5 px-3 py-2 text-[0.9375rem] text-papel placeholder:text-papel/55"
        />
        {texto ? (
          <button
            type="button"
            onClick={limpiar}
            className="shrink-0 rounded-[4px] px-2 py-2 text-[0.875rem] font-medium text-papel/80 hover:text-papel"
          >
            Limpiar
          </button>
        ) : null}
      </div>
    </form>
  );
}
