"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { usePathname, useRouter } from "next/navigation";

const PAUSA_DE_TECLADO_MS = 350;

type Propiedades = {
  criterioInicial: string;
};

export function BuscadorClientes({ criterioInicial }: Propiedades) {
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
    // página anterior, que rara vez tiene coincidencias (FR-024).
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
    <form role="search" onSubmit={alConfirmar} className="w-full sm:w-72">
      <label htmlFor="buscador-clientes" className="sr-only">
        Buscar clientes por razón social
      </label>
      <div className="relative flex items-center">
        <input
          id="buscador-clientes"
          type="search"
          value={texto}
          onChange={alTeclear}
          placeholder="Buscar por razón social"
          autoComplete="off"
          className="w-full rounded-lg border border-[#c6c6cd] bg-white px-3 py-2 text-sm text-[#0b1c30] placeholder:text-[#545f73] focus:border-[#131b2e] focus:outline-none focus:ring-1 focus:ring-[#131b2e]"
        />
        {texto ? (
          <button
            type="button"
            onClick={limpiar}
            className="absolute right-2 shrink-0 rounded px-1.5 py-0.5 text-xs font-semibold text-[#545f73] hover:text-[#0b1c30]"
          >
            Limpiar
          </button>
        ) : null}
      </div>
    </form>
  );
}
