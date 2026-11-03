"use client";

import { Plus } from "lucide-react";
import { useState } from "react";

import { DialogoRendicion } from "@/features/rendiciones/components/dialogo-rendicion";
import type { ServicioElegible } from "@/features/rendiciones/types";

export function NuevaRendicion({ servicios }: { servicios: ServicioElegible[] }) {
  const [abierto, setAbierto] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setAbierto(true)}
        disabled={servicios.length === 0}
        title={
          servicios.length === 0
            ? "No hay servicios finalizados con chofer sin rendición"
            : undefined
        }
        className="flex items-center gap-2 rounded-xl bg-[#2165d5] px-4 py-2.5 text-xs font-bold text-white shadow-[0_5px_12px_rgba(33,101,213,0.18)] transition hover:bg-[#1857bd] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-[#2563eb] dark:hover:bg-[#1d4ed8]"
      >
        <Plus size={16} />
        <span>Nueva rendición</span>
      </button>
      {abierto ? (
        <DialogoRendicion servicios={servicios} onCerrar={() => setAbierto(false)} />
      ) : null}
    </>
  );
}
