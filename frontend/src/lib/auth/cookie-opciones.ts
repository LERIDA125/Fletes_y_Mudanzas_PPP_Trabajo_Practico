export const DURACION_SESION_POR_DEFECTO_SEGUNDOS = 30 * 60;

export type OpcionesCookieSesion = {
  httpOnly: true;
  sameSite: "lax";
  secure: boolean;
  path: "/";
  maxAge: number;
};

/**
 * Opciones de la cookie de sesión. La expiración se alinea con la del JWT
 * (FR-012): si el backend informa una vigencia inválida se usa el TTL de 30
 * minutos del contrato de autenticación.
 */
export function opcionesCookieSesion(expiresIn: number): OpcionesCookieSesion {
  const maxAge =
    Number.isFinite(expiresIn) && expiresIn > 0
      ? Math.floor(expiresIn)
      : DURACION_SESION_POR_DEFECTO_SEGUNDOS;

  return {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge,
  };
}
