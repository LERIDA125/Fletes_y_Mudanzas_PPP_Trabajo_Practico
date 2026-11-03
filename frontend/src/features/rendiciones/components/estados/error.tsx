"use client";

import { useRouter } from "next/navigation";

import type { ClaseDeError } from "@/lib/api/http";

const MENSAJES: Record<ClaseDeError, { titulo: string; detalle: string }> = {
  "sesion-expirada": {
    titulo: "Tu sesión expiró.",
    detalle: "Volvé a iniciar sesión para seguir trabajando.",
  },
  "sin-permisos": {
    titulo: "No tenés permisos para ver las rendiciones.",
    detalle: "Consultá con el administrador del sistema.",
  },
  "error-de-servicio": {
    titulo: "No pudimos leer las rendiciones.",
    detalle: "El sistema rechazó el pedido. Probá de nuevo en un momento.",
  },
  "sin-respuesta": {
    titulo: "No pudimos conectar con el sistema.",
    detalle: "Revisá que el servidor esté funcionando y volvé a intentar.",
  },
};

export function EstadoError({ clase }: { clase: ClaseDeError }) {
  const router = useRouter();
  const mensaje = MENSAJES[clase];

  return (
    <div role="alert" className="py-10 text-center">
      <p className="text-base font-semibold text-[#172b4d] dark:text-white">
        {mensaje.titulo}
      </p>
      <p className="mt-2 text-sm text-[#7f8da1] dark:text-[#94a3b8]">{mensaje.detalle}</p>
      <button
        type="button"
        onClick={() => router.refresh()}
        className="mt-5 rounded-lg border border-[#dfe6ef] px-4 py-2 text-sm font-semibold text-[#62738a] hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:text-[#94a3b8] dark:hover:bg-[#16253d]"
      >
        Reintentar
      </button>
    </div>
  );
}
