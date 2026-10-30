import { cookies } from "next/headers";

import { COOKIE_SESION } from "./constantes";
import { opcionesCookieSesion } from "./cookie-opciones";

export async function leerTokenSesion(): Promise<string | null> {
  const almacen = await cookies();
  return almacen.get(COOKIE_SESION)?.value ?? null;
}

export async function guardarTokenSesion(
  accessToken: string,
  expiresIn: number,
): Promise<void> {
  const almacen = await cookies();
  almacen.set(COOKIE_SESION, accessToken, opcionesCookieSesion(expiresIn));
}

export async function borrarTokenSesion(): Promise<void> {
  const almacen = await cookies();
  almacen.delete(COOKIE_SESION);
}
