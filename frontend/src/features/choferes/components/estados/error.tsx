"use client";

import { useRouter } from "next/navigation";

import type { ClaseDeError } from "@/lib/api/http";

const MENSAJES: Record<ClaseDeError, { titulo: string; detalle: string }> = {
  "sesion-expirada": {
    titulo: "Tu sesión expiró.",
    detalle: "Volvé a iniciar sesión para seguir trabajando.",
  },
  "sin-permisos": {
    titulo: "No tenés permisos para ver este listado.",
    detalle: "Consultá con el administrador del sistema.",
  },
  "error-de-servicio": {
    titulo: "No pudimos leer los choferes.",
    detalle: "El sistema rechazó el pedido. Probá de nuevo en un momento.",
  },
  "sin-respuesta": {
    titulo: "No pudimos conectar con el sistema.",
    detalle: "Revisá que el servidor esté funcionando y volvé a intentar.",
  },
};

type Propiedades = {
  clase: ClaseDeError;
};

export function EstadoError({ clase }: Propiedades) {
  const router = useRouter();
  const mensaje = MENSAJES[clase];

  return (
    <div role="alert" className="border-t border-linea px-4 py-12 sm:px-0">
      <p className="text-[1rem] font-semibold text-alerta">{mensaje.titulo}</p>
      <p className="mt-2 text-[0.875rem] text-tinta-media">{mensaje.detalle}</p>
      <button
        type="button"
        onClick={() => router.refresh()}
        className="mt-5 rounded-[4px] border border-alerta px-4 py-2 text-[0.875rem] font-medium text-alerta hover:bg-alerta hover:text-white"
      >
        Reintentar
      </button>
    </div>
  );
}
