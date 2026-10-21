const URL_POR_DEFECTO = "http://localhost:8000";

export type ClaseDeError =
  "sesion-expirada" | "sin-permisos" | "error-de-servicio" | "sin-respuesta";

export class ErrorApi extends Error {
  readonly status: number | null;
  readonly clase: ClaseDeError;
  readonly detalle: unknown;

  constructor(mensaje: string, opciones: { status?: number | null; detalle?: unknown }) {
    super(mensaje);
    this.name = "ErrorApi";
    this.status = opciones.status ?? null;
    this.detalle = opciones.detalle ?? null;
    this.clase = clasificar(this.status);
  }
}

function clasificar(status: number | null): ClaseDeError {
  if (status === null) {
    return "sin-respuesta";
  }
  if (status === 401) {
    return "sesion-expirada";
  }
  if (status === 403) {
    return "sin-permisos";
  }
  return "error-de-servicio";
}

export function resolverBaseUrl(): string {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL ?? URL_POR_DEFECTO;
  }
  return process.env.API_URL ?? URL_POR_DEFECTO;
}

async function leerDetalle(res: Response): Promise<unknown> {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

export async function request<T>(ruta: string, init?: RequestInit): Promise<T> {
  const url = new URL(ruta, `${resolverBaseUrl()}/`);

  let res: Response;
  try {
    res = await fetch(url, init);
  } catch (error) {
    throw new ErrorApi("No se pudo conectar con el sistema.", {
      status: null,
      detalle: error,
    });
  }

  if (!res.ok) {
    const detalle = await leerDetalle(res);
    throw new ErrorApi(`La API respondió con ${res.status}.`, {
      status: res.status,
      detalle,
    });
  }

  return (await res.json()) as T;
}
