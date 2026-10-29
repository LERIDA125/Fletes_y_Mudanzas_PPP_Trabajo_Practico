import type { components } from "@/types/openapi";
import { request } from "./http";

export type LoginRequest = components["schemas"]["LoginRequest"];
export type TokenResponse = components["schemas"]["TokenRead"];
export type UsuarioCreate = components["schemas"]["UsuarioCreate"];
export type UsuarioRead = components["schemas"]["UsuarioRead"];
export type UsuarioListado = UsuarioRead[];

export const CLAVE_TOKEN_JWT = "fletes_jwt_token";
export const CLAVE_USUARIO_SESION = "fletes_usuario_sesion";

export function guardarSesionCliente(respuesta: TokenResponse): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(CLAVE_TOKEN_JWT, respuesta.access_token);
  window.localStorage.setItem(CLAVE_USUARIO_SESION, JSON.stringify(respuesta.usuario));
  window.dispatchEvent(new Event("storage"));
}

export function limpiarSesionCliente(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(CLAVE_TOKEN_JWT);
  window.localStorage.removeItem(CLAVE_USUARIO_SESION);
  window.dispatchEvent(new Event("storage"));
}

export function obtenerUsuarioSesionLocal(): UsuarioRead | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    const raw = window.localStorage.getItem(CLAVE_USUARIO_SESION);
    if (!raw) {
      return null;
    }
    return JSON.parse(raw) as UsuarioRead;
  } catch {
    return null;
  }
}

export async function iniciarSesionApi(
  credenciales: LoginRequest,
): Promise<TokenResponse> {
  return request<TokenResponse>("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credenciales),
  });
}

export async function obtenerPerfilActualApi(token?: string): Promise<UsuarioRead> {
  const headers: Record<string, string> = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return request<UsuarioRead>("/api/auth/me", { headers });
}

export async function listarUsuariosApi(token?: string): Promise<UsuarioRead[]> {
  const headers: Record<string, string> = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return request<UsuarioRead[]>("/api/auth/usuarios", { headers });
}

export async function crearUsuarioApi(
  datos: UsuarioCreate,
  token?: string,
): Promise<UsuarioRead> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return request<UsuarioRead>("/api/auth/usuarios", {
    method: "POST",
    headers,
    body: JSON.stringify(datos),
  });
}
