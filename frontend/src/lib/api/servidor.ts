import { leerTokenSesion } from "@/lib/auth/session";

import { request } from "./http";

/**
 * Wrapper server-only para llamar a la API protegida. El JWT se lee de la
 * cookie httpOnly y se reenvía como Bearer; nunca se expone al navegador
 * (FR-009/FR-010).
 */
export async function requestAutenticado<T>(
  ruta: string,
  init?: RequestInit,
): Promise<T> {
  const token = await leerTokenSesion();
  const headers = new Headers(init?.headers);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return request<T>(ruta, { ...init, headers });
}
