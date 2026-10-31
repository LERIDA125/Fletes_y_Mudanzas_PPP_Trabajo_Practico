import { afterEach, describe, expect, it, vi } from "vitest";

import {
  DURACION_SESION_POR_DEFECTO_SEGUNDOS,
  opcionesCookieSesion,
} from "@/lib/auth/cookie-opciones";
import { rutaInicialPorRol } from "@/lib/auth/rutas";

describe("opcionesCookieSesion", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("usa httpOnly, sameSite lax, path raíz y expira con el token", () => {
    vi.stubEnv("NODE_ENV", "development");

    expect(opcionesCookieSesion(1800)).toEqual({
      httpOnly: true,
      sameSite: "lax",
      secure: false,
      path: "/",
      maxAge: 1800,
    });
  });

  it("marca la cookie como secure en producción", () => {
    vi.stubEnv("NODE_ENV", "production");

    expect(opcionesCookieSesion(1800).secure).toBe(true);
  });

  it("cae al TTL de 30 minutos si la vigencia informada no es válida", () => {
    vi.stubEnv("NODE_ENV", "development");

    expect(opcionesCookieSesion(0).maxAge).toBe(DURACION_SESION_POR_DEFECTO_SEGUNDOS);
    expect(opcionesCookieSesion(Number.NaN).maxAge).toBe(
      DURACION_SESION_POR_DEFECTO_SEGUNDOS,
    );
  });
});

describe("rutaInicialPorRol", () => {
  it("envía al chofer a su dashboard placeholder", () => {
    expect(rutaInicialPorRol("CHOFER")).toBe("/chofer/dashboard");
    expect(rutaInicialPorRol("chofer")).toBe("/chofer/dashboard");
  });

  it("envía al administrador al dashboard existente en /", () => {
    expect(rutaInicialPorRol("ADMIN")).toBe("/");
    expect(rutaInicialPorRol("admin")).toBe("/");
  });
});
