import { redirect } from "next/navigation";

import { ErrorApi, request } from "@/lib/api/http";

import { RUTA_LOGIN, rutaInicialPorRol } from "./rutas";
import { leerTokenSesion } from "./session";
import type { RolSesion, UsuarioSesion } from "./tipos";

/**
 * Resuelve la identidad contra la API con un token explícito. Un 401 significa
 * que la sesión ya no es válida; cualquier otra falla se propaga para no
 * conceder acceso cuando el backend no responde (FR-011).
 */
export async function obtenerUsuarioConToken(
  token: string,
): Promise<UsuarioSesion | null> {
  try {
    return await request<UsuarioSesion>("/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch (error) {
    if (error instanceof ErrorApi && error.status === 401) {
      return null;
    }
    throw error;
  }
}

export async function obtenerUsuarioActual(): Promise<UsuarioSesion | null> {
  const token = await leerTokenSesion();
  if (!token) {
    return null;
  }
  return obtenerUsuarioConToken(token);
}

/**
 * Guard server-side de rol. Redirige a login si no hay sesión y al dashboard
 * del rol real si la sesión no corresponde al rol exigido.
 */
export async function exigirRol(rol: RolSesion): Promise<UsuarioSesion> {
  const usuario = await obtenerUsuarioActual();

  if (!usuario) {
    redirect(RUTA_LOGIN);
  }

  if (usuario.rol.toUpperCase() !== rol) {
    redirect(rutaInicialPorRol(usuario.rol));
  }

  return usuario;
}
