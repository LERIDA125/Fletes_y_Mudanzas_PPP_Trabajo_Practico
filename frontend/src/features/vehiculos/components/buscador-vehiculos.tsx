"use client";

import { Search } from "lucide-react";
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
    <form role="search" onSubmit={alConfirmar} className="w-full sm:w-72">
      <label htmlFor="buscador-vehiculos" className="sr-only">
        Buscar vehículos por patente
      </label>
      <div className="relative flex items-center">
        <Search className="pointer-events-none absolute left-3 size-4 text-slate-400 dark:text-slate-500" />
        <input
          id="buscador-vehiculos"
          type="search"
          value={texto}
          onChange={alTeclear}
          placeholder="Buscar por patente"
          autoComplete="off"
          className="w-full rounded-lg border border-slate-200 bg-white pl-9 pr-8 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-950 focus:outline-none focus:ring-1 focus:ring-slate-950 dark:border-[#1e2c44] dark:bg-[#111c2e] dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:border-slate-100 dark:focus:ring-slate-100"
        />
        {texto ? (
          <button
            type="button"
            onClick={limpiar}
            className="absolute right-2 shrink-0 rounded px-1.5 py-0.5 text-xs font-semibold text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
          >
            Limpiar
          </button>
        ) : null}
      </div>
    </form>
  );
}
