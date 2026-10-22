import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { BuscadorClientes } from "@/features/clientes/components/buscador-clientes";

const empujar = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: empujar, refresh: vi.fn() }),
  usePathname: () => "/",
}));

const PAUSA = 350;

function escribir(texto: string) {
  const campo = screen.getByLabelText("Buscar clientes por razón social");
  fireEvent.change(campo, { target: { value: texto } });
}

describe("BuscadorClientes", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    empujar.mockClear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("espera la pausa de tecleo antes de buscar (FR-015)", () => {
    render(<BuscadorClientes criterioInicial="" />);

    escribir("distribu");
    expect(empujar).not.toHaveBeenCalled();

    act(() => {
      vi.advanceTimersByTime(PAUSA - 1);
    });
    expect(empujar).not.toHaveBeenCalled();

    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(empujar).toHaveBeenCalledExactlyOnceWith("/?q=distribu");
  });

  it("reinicia el temporizador si el usuario sigue tecleando", () => {
    render(<BuscadorClientes criterioInicial="" />);

    escribir("dis");
    act(() => {
      vi.advanceTimersByTime(PAUSA - 100);
    });
    escribir("distribu");
    act(() => {
      vi.advanceTimersByTime(PAUSA - 1);
    });

    expect(empujar).not.toHaveBeenCalled();

    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(empujar).toHaveBeenCalledExactlyOnceWith("/?q=distribu");
  });

  it("Enter busca de inmediato, sin esperar la pausa", () => {
    render(<BuscadorClientes criterioInicial="" />);

    escribir("sur");
    fireEvent.submit(screen.getByRole("search"));

    expect(empujar).toHaveBeenCalledExactlyOnceWith("/?q=sur");
  });

  it("descarta espacios al confirmar con Enter", () => {
    render(<BuscadorClientes criterioInicial="" />);

    escribir("  sur  ");
    fireEvent.submit(screen.getByRole("search"));

    expect(empujar).toHaveBeenCalledExactlyOnceWith("/?q=sur");
  });

  it("vuelve a la primera página al cambiar el criterio (FR-024)", () => {
    render(<BuscadorClientes criterioInicial="" />);

    escribir("sur");
    act(() => {
      vi.advanceTimersByTime(PAUSA);
    });

    // La URL que arma el componente nunca arrastra la página anterior:
    // un criterio nuevo siempre empieza en 1.
    expect(empujar.mock.calls[0][0]).not.toContain("page=");
  });

  it("limpiar el campo borra el criterio de la URL", () => {
    render(<BuscadorClientes criterioInicial="sur" />);

    fireEvent.click(screen.getByRole("button", { name: "Limpiar" }));

    expect(empujar).toHaveBeenCalledExactlyOnceWith("/");
  });

  it("muestra el botón de limpiar solo si hay texto", () => {
    const { rerender } = render(<BuscadorClientes criterioInicial="" />);
    expect(screen.queryByRole("button", { name: "Limpiar" })).toBeNull();

    rerender(<BuscadorClientes criterioInicial="sur" />);
    expect(screen.getByRole("button", { name: "Limpiar" })).toBeInTheDocument();
  });
});
