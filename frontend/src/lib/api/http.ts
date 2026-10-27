// Dentro de Docker Compose el backend se llama `backend`; en desarrollo local
// sobre el host se llega por `localhost`. El servidor de Next prueba primero la
// URL configurada y luego ambos hosts conocidos, para que un `API_URL`
// ausente o mal configurado no deje toda la UI sin datos.
const URL_SERVIDOR_POR_DEFECTO = "http://backend:8000";
const URL_LOCAL_POR_DEFECTO = "http://localhost:8000";
const TIMEOUT_MS_POR_DEFECTO = 10_000;

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

function normalizarBaseUrl(valor: string | undefined): string | null {
  const limpio = valor?.trim();
  if (!limpio) {
    return null;
  }
  return limpio.replace(/\/+$/, "");
}

function unicos(valores: Array<string | null>): string[] {
  return [...new Set(valores.filter((valor): valor is string => valor !== null))];
}

/**
 * URLs candidatas en orden de preferencia.
 *
 * En el servidor la prioridad es `API_URL` (URL interna, p. ej. el nombre del
 * servicio de Docker) y luego los hosts por defecto. En el navegador solo tiene
 * sentido la URL pública (`NEXT_PUBLIC_API_URL`) porque no resuelve `backend`.
 */
export function resolverBaseUrls(): string[] {
  if (typeof window !== "undefined") {
    return unicos([
      normalizarBaseUrl(process.env.NEXT_PUBLIC_API_URL),
      URL_LOCAL_POR_DEFECTO,
    ]);
  }
  return unicos([
    normalizarBaseUrl(process.env.API_URL),
    URL_SERVIDOR_POR_DEFECTO,
    normalizarBaseUrl(process.env.NEXT_PUBLIC_API_URL),
    URL_LOCAL_POR_DEFECTO,
  ]);
}

export function resolverBaseUrl(): string {
  return resolverBaseUrls()[0] ?? URL_LOCAL_POR_DEFECTO;
}

async function leerDetalle(res: Response): Promise<unknown> {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

function describirDetalle(detalle: unknown): string | null {
  if (!detalle || typeof detalle !== "object") {
    return null;
  }
  const cuerpo = detalle as Record<string, unknown>;
  const mensaje = cuerpo.detail ?? cuerpo.message;
  if (typeof mensaje === "string" && mensaje.trim()) {
    return mensaje;
  }
  // FastAPI devuelve `detail` como lista de errores de validación.
  if (Array.isArray(mensaje)) {
    const partes = mensaje
      .map((item) => {
        if (!item || typeof item !== "object") {
          return null;
        }
        const error = item as Record<string, unknown>;
        const ubicacion = Array.isArray(error.loc) ? error.loc.join(".") : "";
        const texto = typeof error.msg === "string" ? error.msg : "";
        if (!texto) {
          return null;
        }
        return ubicacion ? `${ubicacion}: ${texto}` : texto;
      })
      .filter((parte): parte is string => Boolean(parte));
    if (partes.length > 0) {
      return partes.join("; ");
    }
  }
  return null;
}

function esCortePorTiempo(error: unknown): boolean {
  if (!error || typeof error !== "object" || !("name" in error)) {
    return false;
  }
  const nombre = (error as { name?: unknown }).name;
  return nombre === "TimeoutError" || nombre === "AbortError";
}

export async function request<T>(ruta: string, init?: RequestInit): Promise<T> {
  // Los datos del sistema cambian desde la UI; nunca servir una respuesta cacheada.
  const headers = new Headers(init?.headers);
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }
  if (init?.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  // Inyección global del rol para autorizar las peticiones en FastAPI
  if (!headers.has("X-Rol")) {
    headers.set("X-Rol", "admin");
  }

  let res: Response | null = null;
  let ultimoError: unknown = null;
  const intentos: string[] = [];
  const metodo = (init?.method ?? "GET").toUpperCase();
  // Un timeout en un POST es ambiguo: el backend pudo haber creado el recurso.
  // Solo los métodos seguros/idempotentes se reintentan tras un timeout.
  const reintentarAnteTimeout = metodo === "GET" || metodo === "HEAD";

  // Un fallo de red (DNS, conexión rechazada o timeout) no debería dejar la UI
  // sin datos si el backend está accesible por otro de los hosts conocidos.
  // Los errores HTTP no se reintentan: la API respondió y su detalle es válido.
  for (const base of resolverBaseUrls()) {
    try {
      const url = new URL(ruta, `${base}/`);
      intentos.push(url.toString());
      const timeoutSignal = AbortSignal.timeout(TIMEOUT_MS_POR_DEFECTO);
      const signal = init?.signal
        ? AbortSignal.any([init.signal, timeoutSignal])
        : timeoutSignal;
      res = await fetch(url, {
        ...init,
        headers,
        cache: "no-store",
        signal,
      });
      break;
    } catch (error) {
      ultimoError = error;
      // Si quien llamó abortó la petición, no tiene sentido probar otro host.
      if (init?.signal?.aborted) {
        break;
      }
      if (esCortePorTiempo(error) && !reintentarAnteTimeout) {
        break;
      }
    }
  }

  if (!res) {
    if (typeof window === "undefined") {
      console.error(
        `[api] No se pudo conectar con el backend. Intentos: ${intentos.join(" | ")}`,
        ultimoError,
      );
    }
    throw new ErrorApi("No se pudo conectar con el sistema.", {
      status: null,
      detalle: { intentos, causa: ultimoError },
    });
  }

  if (!res.ok) {
    const detalle = await leerDetalle(res);
    const mensaje = describirDetalle(detalle) ?? `La API respondió con ${res.status}.`;
    throw new ErrorApi(mensaje, { status: res.status, detalle });
  }

  if (res.status === 204 || res.headers.get("content-length") === "0") {
    return undefined as T;
  }

  const texto = await res.text();
  if (!texto) {
    return undefined as T;
  }

  try {
    return JSON.parse(texto) as T;
  } catch {
    return texto as unknown as T;
  }
}
