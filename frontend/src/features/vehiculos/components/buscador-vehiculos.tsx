"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { usePathname, useRouter } from "next/navigation";

const PAUSA_DE_TECLADO_MS = 350;

type Propiedades = {
  criterioInicial: string;
};

export function BuscadorVehiculos({ criterioInicial }: Propiedades) {
  const router = useRouter();
  const pathname = usePathname();
  const [texto, setTexto] = useState(criterioInicial);
  const temporizador = useRef<ReturnType<typeof setTimeout> | null>(null);

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
      <label htmlFor="buscador-vehiculos" className="sr-only">
        Buscar vehículos por patente
      </label>
      <div className="flex items-center gap-2">
        <input
          id="buscador-vehiculos"
          type="search"
          value={texto}
          onChange={alTeclear}
          placeholder="Buscar por patente"
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
