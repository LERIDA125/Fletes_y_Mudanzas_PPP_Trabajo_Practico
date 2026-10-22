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
    <div
      role="alert"
      className="rounded-lg border border-red-200 bg-panel-superficie px-5 py-8"
    >
      <p className="text-base font-semibold text-red-700">{mensaje.titulo}</p>
      <p className="mt-2 text-sm text-panel-secundario">{mensaje.detalle}</p>
      <button
        type="button"
        onClick={() => router.refresh()}
        className="mt-5 inline-flex min-h-10 items-center rounded-md border border-red-200 px-4 text-sm font-medium text-red-700 hover:bg-red-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul"
      >
        Reintentar
      </button>
    </div>
  );
}
