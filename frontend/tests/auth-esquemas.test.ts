import { describe, expect, it } from "vitest";

import { esquemaLogin } from "@/features/auth/schemas/login";
import { esquemaUsuario } from "@/features/usuarios/schemas/usuario";

describe("esquemaLogin", () => {
  it("normaliza el username y acepta credenciales completas", () => {
    const resultado = esquemaLogin.safeParse({
      username: "  Admin  ",
      password: "una-clave-segura",
    });

    expect(resultado.success).toBe(true);
    expect(resultado.success && resultado.data.username).toBe("Admin");
  });

  it("rechaza usuario o contraseña vacíos", () => {
    expect(esquemaLogin.safeParse({ username: "   ", password: "clave" }).success).toBe(
      false,
    );
    expect(esquemaLogin.safeParse({ username: "admin", password: "" }).success).toBe(
      false,
    );
  });
});

describe("esquemaUsuario", () => {
  const base = {
    username: "juan.perez",
    password: "una-clave-segura-123",
    rol: "ADMIN" as const,
    id_chofer: null,
  };

  it("acepta una cuenta ADMIN sin chofer", () => {
    expect(esquemaUsuario.safeParse(base).success).toBe(true);
  });

  it("exige chofer para una cuenta CHOFER", () => {
    expect(
      esquemaUsuario.safeParse({ ...base, rol: "CHOFER", id_chofer: null }).success,
    ).toBe(false);
    expect(
      esquemaUsuario.safeParse({ ...base, rol: "CHOFER", id_chofer: 12 }).success,
    ).toBe(true);
  });

  it("rechaza contraseñas fuera de la política", () => {
    expect(esquemaUsuario.safeParse({ ...base, password: "corta" }).success).toBe(false);
  });

  it("rechaza una contraseña igual al nombre de usuario", () => {
    const username = "juan.perez.1234";

    expect(
      esquemaUsuario.safeParse({
        ...base,
        username,
        password: username,
      }).success,
    ).toBe(false);
  });
});
