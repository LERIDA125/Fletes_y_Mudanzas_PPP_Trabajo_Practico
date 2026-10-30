import { NextResponse, type NextRequest } from "next/server";

import { COOKIE_SESION } from "@/lib/auth/constantes";
import { RUTA_LOGIN } from "@/lib/auth/rutas";

/**
 * Redirección optimista por presencia de cookie. No es la frontera de
 * autorización: cada layout y Server Action vuelve a validar el JWT y el rol
 * contra la API (FR-011).
 */
export function proxy(request: NextRequest) {
  const token = request.cookies.get(COOKIE_SESION)?.value;

  if (token) {
    return NextResponse.next();
  }

  const url = new URL(RUTA_LOGIN, request.url);
  const destino = request.nextUrl.pathname + request.nextUrl.search;

  if (destino !== "/") {
    url.searchParams.set("destino", destino);
  }

  return NextResponse.redirect(url);
}

export const config = {
  matcher: ["/((?!login|_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};
