export const RUTA_LOGIN = "/login";
export const RUTA_DASHBOARD_ADMIN = "/";
export const RUTA_DASHBOARD_CHOFER = "/chofer/dashboard";

/**
 * Destino inicial según el rol persistido en la API. El dashboard
 * administrativo existente vive en `/` dentro del grupo `(admin)`.
 */
export function rutaInicialPorRol(rol: string): string {
  return rol?.toUpperCase() === "CHOFER" ? RUTA_DASHBOARD_CHOFER : RUTA_DASHBOARD_ADMIN;
}
