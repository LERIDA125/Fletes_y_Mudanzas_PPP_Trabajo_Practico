import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Paginacion } from "@/features/clientes/components/paginacion";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

describe("Paginacion", () => {
  it("no se dibuja cuando todo cabe en una sola página (FR-013)", () => {
    const { container } = render(<Paginacion paginaActual={1} paginas={1} criterio="" />);
    expect(container).toBeEmptyDOMElement();
  });

  it("oculta «Anterior» en la primera página", () => {
    render(<Paginacion paginaActual={1} paginas={3} criterio="" />);
    expect(screen.queryByRole("link", { name: "Anterior" })).toBeNull();
    expect(screen.getByRole("link", { name: "Siguiente" })).toBeInTheDocument();
  });

  it("oculta «Siguiente» en la última página", () => {
    render(<Paginacion paginaActual={3} paginas={3} criterio="" />);
    expect(screen.queryByRole("link", { name: "Siguiente" })).toBeNull();
    expect(screen.getByRole("link", { name: "Anterior" })).toBeInTheDocument();
  });

  it("marca la página actual con aria-current", () => {
    render(<Paginacion paginaActual={2} paginas={3} criterio="" />);

    const actual = screen.getByRole("link", { name: "2" });
    expect(actual).toHaveAttribute("aria-current", "page");

    const otra = screen.getByRole("link", { name: "1" });
    expect(otra).not.toHaveAttribute("aria-current");
  });

  it("la primera página vive en la raíz, sin parámetros", () => {
    render(<Paginacion paginaActual={1} paginas={3} criterio="" />);
    expect(screen.getByRole("link", { name: "1" })).toHaveAttribute("href", "/");
  });

  it("conserva el criterio de búsqueda en cada enlace", () => {
    render(<Paginacion paginaActual={2} paginas={3} criterio="sur" />);
    expect(screen.getByRole("link", { name: "1" })).toHaveAttribute("href", "/?q=sur");
    expect(screen.getByRole("link", { name: "3" })).toHaveAttribute(
      "href",
      "/?q=sur&page=3",
    );
  });

  it("ventana de páginas acotada con muchas páginas", () => {
    render(<Paginacion paginaActual={10} paginas={50} criterio="" />);
    const numeritos = screen
      .getAllByRole("link")
      .map((enlace) => enlace.textContent)
      .filter((texto) => /^\d+$/.test(texto ?? ""));
    expect(numeritos).toEqual(["8", "9", "10", "11", "12"]);
  });
});
