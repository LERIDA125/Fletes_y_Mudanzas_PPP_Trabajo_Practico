"use server";

import { revalidatePath } from "next/cache";

import { ErrorApi } from "@/lib/api/http";
import { requestAutenticado } from "@/lib/api/servidor";
import { exigirRol } from "@/lib/auth/guards";
import type { components } from "@/types/openapi";

import { esquemaUsuario } from "./schemas/usuario";

export type UsuarioCreado = components["schemas"]["UsuarioRead"];

export type ResultadoCrearUsuario =
  { ok: true; usuario: UsuarioCreado } | { ok: false; mensaje: string };

export type DatosNuevoUsuario = {
  username: string;
  password: string;
  rol: string;
  id_chofer: number | null;
};

/**
 * Alta administrativa de cuentas. El Server Action revalida el rol ADMIN y la
 * API vuelve a aplicar su propia autorización sobre el Bearer (FR-018).
 */
export async function crearUsuario(
  datos: DatosNuevoUsuario,
): Promise<ResultadoCrearUsuario> {
  await exigirRol("ADMIN");

  const validacion = esquemaUsuario.safeParse({
    ...datos,
    id_chofer: datos.rol === "CHOFER" ? datos.id_chofer : null,
  });

  if (!validacion.success) {
    return {
      ok: false,
      mensaje: validacion.error.issues[0]?.message ?? "Revisá los datos ingresados.",
    };
  }

  const payload: components["schemas"]["UsuarioCreate"] = {
    username: validacion.data.username,
    password: validacion.data.password,
    rol: validacion.data.rol,
    id_chofer:
      validacion.data.rol === "CHOFER" ? (validacion.data.id_chofer ?? null) : null,
  };

  try {
    const usuario = await requestAutenticado<UsuarioCreado>("/api/usuarios", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    revalidatePath("/usuarios");
    return { ok: true, usuario };
  } catch (error) {
    if (error instanceof ErrorApi) {
      return { ok: false, mensaje: mensajeDeError(error) };
    }
    throw error;
  }
}

function mensajeDeError(error: ErrorApi): string {
  if (error.clase === "sesion-expirada") {
    return "Tu sesión venció. Volvé a iniciar sesión.";
  }
  if (error.clase === "sin-permisos") {
    return "Solo un administrador puede crear cuentas de usuario.";
  }
  if (error.clase === "sin-respuesta") {
    return "No pudimos conectar con el sistema. Intentá de nuevo.";
  }
  if (error.status === 409) {
    if (/chofer/i.test(error.message)) {
      return "Ese chofer ya tiene una cuenta asignada.";
    }
    if (/username|usuario/i.test(error.message)) {
      return "Ese nombre de usuario ya está en uso.";
    }
    return error.message || "No se pudo crear la cuenta.";
  }
  if (error.status === 422) {
    return error.message || "Revisá los datos ingresados.";
  }
  return "No pudimos crear la cuenta. Intentá de nuevo.";
}
