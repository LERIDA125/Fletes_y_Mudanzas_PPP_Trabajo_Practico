"use client";

import { useState } from "react";

import { DialogoCliente } from "./dialogo-cliente";

export function NuevoCliente() {
  const [abierto, setAbierto] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setAbierto(true)}
        className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-orange-200 transition-all hover:bg-orange-600 active:scale-[0.99] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500"
      >
        <span className="text-base font-bold leading-none" aria-hidden="true">
          +
        </span>
        <span>Nuevo cliente</span>
      </button>
      {abierto ? <DialogoCliente onCerrar={() => setAbierto(false)} /> : null}
    </>
  );
}
