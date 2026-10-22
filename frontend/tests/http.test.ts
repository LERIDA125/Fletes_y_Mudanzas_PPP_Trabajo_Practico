import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ErrorApi, request } from "@/lib/api/http";

const fetchFalso = vi.fn();

function responder(status: number, cuerpo: unknown = null) {
  return new Response(cuerpo === null ? null : JSON.stringify(cuerpo), { status });
}

describe("request", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", fetchFalso);
    fetchFalso.mockReset();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("resuelve con el JSON cuando la API responde bien", async () => {
    fetchFalso.mockResolvedValue(responder(200, { items: [], total: 0 }));

    await expect(request("/api/clientes")).resolves.toEqual({ items: [], total: 0 });
  });

  it("mapea 401 a sesión expirada (FR-016)", async () => {
    fetchFalso.mockResolvedValue(responder(401, { detail: "expirado" }));

    await expect(request("/api/clientes")).rejects.toMatchObject({
      name: "ErrorApi",
      status: 401,
      clase: "sesion-expirada",
    });
  });

  it("mapea 403 a falta de permisos", async () => {
    fetchFalso.mockResolvedValue(responder(403));

    await expect(request("/api/clientes")).rejects.toMatchObject({
      clase: "sin-permisos",
    });
  });

  it("mapea 500 a error de servicio y conserva el detalle", async () => {
    fetchFalso.mockResolvedValue(responder(500, { detail: "boom" }));

    const error = await request("/api/clientes").catch((capturado: unknown) => capturado);

    expect(error).toBeInstanceOf(ErrorApi);
    expect(error).toMatchObject({ clase: "error-de-servicio", status: 500 });
    expect((error as ErrorApi).detalle).toEqual({ detail: "boom" });
  });

  it("mapea una falla de red a sin-respuesta, con status null", async () => {
    fetchFalso.mockRejectedValue(new TypeError("Failed to fetch"));

    await expect(request("/api/clientes")).rejects.toMatchObject({
      clase: "sin-respuesta",
      status: null,
    });
  });

  it("no revienta si el cuerpo de error no es JSON", async () => {
    fetchFalso.mockResolvedValue(responder(502, undefined));

    await expect(request("/api/clientes")).rejects.toMatchObject({
      clase: "error-de-servicio",
      detalle: null,
    });
  });
});
