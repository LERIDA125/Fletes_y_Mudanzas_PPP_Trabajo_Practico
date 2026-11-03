"use client";

import { Search } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState, type FormEvent } from "react";

const PAUSA_DE_TECLADO_MS = 350;

export function BuscadorRendiciones({ criterioInicial }: { criterioInicial: string }) {
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
      aplicar(valor.trim());
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
      <label htmlFor="buscador-rendiciones" className="sr-only">
        Buscar rendiciones por código, chofer o servicio
      </label>
      <div className="relative flex items-center rounded-xl border border-[#dfe6ef] bg-[#fbfcfd] px-3 py-1.5 dark:border-[#1e2c44] dark:bg-[#0d1626]">
        <Search className="pointer-events-none size-4 text-[#99a7b8] dark:text-[#64748b]" />
        <input
          id="buscador-rendiciones"
          type="search"
          value={texto}
          onChange={alTeclear}
          placeholder="Buscar por chofer o código..."
          autoComplete="off"
          className="ml-2 w-full bg-transparent text-xs text-[#172b4d] outline-none placeholder:text-[#aab4c1] dark:text-white dark:placeholder:text-[#64748b]"
        />
        {texto ? (
          <button
            type="button"
            onClick={limpiar}
            className="shrink-0 rounded px-1.5 py-0.5 text-xs font-semibold text-[#62738a] hover:text-[#172b4d] dark:text-[#94a3b8] dark:hover:text-white"
          >
            Limpiar
          </button>
        ) : null}
      </div>
    </form>
  );
}
