"use client";

import { LogOut } from "lucide-react";

import { cerrarSesion } from "@/features/auth/actions";

export function BotonCerrarSesion() {
  return (
    <form action={cerrarSesion}>
      <button
        type="submit"
        aria-label="Cerrar sesión"
        title="Cerrar sesión"
        className="inline-flex h-9 items-center gap-2 rounded-xl border border-[#e5eaf1] bg-[#fafcff] px-3 text-xs font-semibold text-[#5f7087] transition hover:border-[#f3c4c4] hover:bg-[#fff1f1] hover:text-[#c0392b] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2165d5] dark:border-[#1e2c44] dark:bg-[#16253d] dark:text-[#94a3b8] dark:hover:border-[#5b2b2b] dark:hover:bg-[#2a1717] dark:hover:text-[#fca5a5]"
      >
        <LogOut aria-hidden="true" size={15} />
        <span className="hidden sm:inline">Salir</span>
      </button>
    </form>
  );
}
