"use client";

import { useRouter } from "next/navigation";

import type { ClaseDeError } from "@/lib/api/http";

const MENSAJES: Record<ClaseDeError, { titulo: string; detalle: string }> = {
  "sesion-expirada": {
    titulo: "No está habilitado el modo de demo.",
    detalle: "Usá el entorno local con ENVIRONMENT=dev y DEV_ASSUME_ADMIN=true.",
  },
  "sin-permisos": {
    titulo: "La API rechazó la solicitud.",
    detalle: "Revisá la configuración de acceso del entorno local.",
  },
  "error-de-servicio": {
    titulo: "No pudimos leer los servicios.",
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
