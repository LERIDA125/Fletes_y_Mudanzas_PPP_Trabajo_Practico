"use server";

import { redirect } from "next/navigation";

import { ErrorApi, request } from "@/lib/api/http";
import { obtenerUsuarioConToken } from "@/lib/auth/guards";
import { rutaInicialPorRol } from "@/lib/auth/rutas";
import { borrarTokenSesion, guardarTokenSesion } from "@/lib/auth/session";
import type { components } from "@/types/openapi";

import { esquemaLogin } from "./schemas/login";

type TokenRespuesta = components["schemas"]["TokenRead"];

export type EstadoLogin = { error?: string };

const MENSAJE_CREDENCIALES = "Usuario o contraseña incorrectos.";
const MENSAJE_SIN_CONEXION =
  "No pudimos conectar con el sistema. Revisá tu conexión e intentá de nuevo.";

/**
 * Server Action de login: valida la forma, autentica contra la API, guarda el
 * JWT en una cookie httpOnly y redirige según el rol real devuelto por `/me`.
 * Los errores de credenciales son genéricos (FR-013).
 */
export async function iniciarSesion(
  _estadoAnterior: EstadoLogin,
  formData: FormData,
): Promise<EstadoLogin> {
  const validacion = esquemaLogin.safeParse({
    username: formData.get("username"),
    password: formData.get("password"),
  });

  if (!validacion.success) {
    return { error: "Ingresá tu usuario y tu contraseña." };
  }

  let token: TokenRespuesta;

  try {
    token = await request<TokenRespuesta>("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(validacion.data),
    });
  } catch (error) {
    if (error instanceof ErrorApi) {
      if (error.clase === "sin-respuesta") {
        return { error: MENSAJE_SIN_CONEXION };
      }
      if (error.status === 401 || error.status === 422) {
        return { error: MENSAJE_CREDENCIALES };
      }
      return {
        error:
          error.message ||
          "El servidor tuvo un problema al procesar el inicio de sesión.",
      };
    }
    throw error;
  }

  await guardarTokenSesion(token.access_token, token.expires_in);

  let destino = "/";

  try {
    const usuario = await obtenerUsuarioConToken(token.access_token);
    if (!usuario) {
      await borrarTokenSesion();
      return { error: "No pudimos iniciar la sesión. Intentá de nuevo." };
    }
    destino = rutaInicialPorRol(usuario.rol);
  } catch {
    // Si `/me` no responde, el guard del layout vuelve a resolver el rol.
  }

  redirect(destino);
}

export async function cerrarSesion(): Promise<void> {
  await borrarTokenSesion();
  redirect("/login");
}
