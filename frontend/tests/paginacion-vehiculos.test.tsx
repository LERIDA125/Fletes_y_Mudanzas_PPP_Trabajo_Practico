import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Paginacion } from "@/features/vehiculos/components/paginacion";

vi.mock("next/navigation", () => ({
  usePathname: () => "/vehiculos",
}));

describe("Paginacion de vehículos", () => {
  it("no aparece cuando el resultado ocupa una página", () => {
    const { container } = render(<Paginacion paginaActual={1} paginas={1} criterio="" />);
    expect(container).toBeEmptyDOMElement();
  });

  it("oculta anterior en la primera página y siguiente en la última", () => {
    const { rerender } = render(<Paginacion paginaActual={1} paginas={3} criterio="" />);
    expect(screen.queryByRole("link", { name: "Anterior" })).toBeNull();
    expect(screen.getByRole("link", { name: "Siguiente" })).toBeInTheDocument();

    rerender(<Paginacion paginaActual={3} paginas={3} criterio="" />);
    expect(screen.getByRole("link", { name: "Anterior" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Siguiente" })).toBeNull();
  });

  it("conserva la búsqueda al navegar y omite page=1", () => {
    render(<Paginacion paginaActual={2} paginas={3} criterio="AA" />);

    expect(screen.getByRole("link", { name: "1" })).toHaveAttribute(
      "href",
      "/vehiculos?q=AA",
    );
    expect(screen.getByRole("link", { name: "3" })).toHaveAttribute(
      "href",
      "/vehiculos?q=AA&page=3",
    );
  });

  it("marca la página actual para tecnologías de asistencia", () => {
    render(<Paginacion paginaActual={2} paginas={3} criterio="" />);

    expect(screen.getByRole("link", { name: "2" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });
});
