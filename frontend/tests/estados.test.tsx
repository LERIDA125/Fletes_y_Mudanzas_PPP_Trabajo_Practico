import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { EstadoError } from "@/features/clientes/components/estados/error";
import { EstadoVacio } from "@/features/clientes/components/estados/vacio";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), refresh: vi.fn() }),
}));

describe("EstadoVacio", () => {
  it("con criterio, nombra el término que no dio resultados (FR-025)", () => {
    render(<EstadoVacio criterio="distribu" rutaSinBusqueda="/" />);

    expect(screen.getByRole("status")).toHaveTextContent(
      "No hay clientes cuya razón social contenga «distribu».",
    );
    expect(screen.getByRole("link", { name: "Limpiar búsqueda" })).toHaveAttribute(
      "href",
      "/",
    );
  });

  it("sin criterio, distingue «sin datos» de «sin coincidencias»", () => {
    render(<EstadoVacio criterio="" rutaSinBusqueda="/" />);

    expect(screen.getByRole("status")).toHaveTextContent(
      "Todavía no hay clientes dados de alta en el sistema.",
    );
    expect(screen.queryByRole("link")).toBeNull();
  });
});

describe("EstadoError", () => {
  it("explica la falla de conexión sin exponer detalles técnicos", () => {
    render(<EstadoError clase="sin-respuesta" />);

    expect(screen.getByRole("alert")).toHaveTextContent(
      "No pudimos conectar con el sistema.",
    );
    expect(screen.getByRole("button", { name: "Reintentar" })).toBeInTheDocument();
  });

  it("usa otro mensaje cuando el servicio rechazó el pedido", () => {
    render(<EstadoError clase="error-de-servicio" />);

    expect(screen.getByRole("alert")).toHaveTextContent("No pudimos leer los clientes.");
    expect(screen.queryByText(/Failed to fetch/i)).toBeNull();
  });
});
