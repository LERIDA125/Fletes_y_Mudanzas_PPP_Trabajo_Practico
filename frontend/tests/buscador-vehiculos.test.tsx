import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { BuscadorVehiculos } from "@/features/vehiculos/components/buscador-vehiculos";

const empujar = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: empujar }),
  usePathname: () => "/vehiculos",
}));

const PAUSA = 350;

function escribir(texto: string) {
  fireEvent.change(screen.getByLabelText("Buscar vehículos por patente"), {
    target: { value: texto },
  });
}

describe("BuscadorVehiculos", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    empujar.mockClear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("espera 350 ms desde la última tecla para aplicar el criterio", () => {
    render(<BuscadorVehiculos criterioInicial="" />);

    escribir("AA 123");
    act(() => {
      vi.advanceTimersByTime(PAUSA - 1);
    });
    expect(empujar).not.toHaveBeenCalled();

    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(empujar).toHaveBeenCalledExactlyOnceWith("/vehiculos?q=AA%20123");
  });

  it("reinicia el debounce mientras el usuario sigue escribiendo", () => {
    render(<BuscadorVehiculos criterioInicial="" />);

    escribir("AA");
    act(() => {
      vi.advanceTimersByTime(PAUSA - 100);
    });
    escribir("AA 123");
    act(() => {
      vi.advanceTimersByTime(PAUSA - 1);
    });
    expect(empujar).not.toHaveBeenCalled();

    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(empujar).toHaveBeenCalledExactlyOnceWith("/vehiculos?q=AA%20123");
  });

  it("Enter aplica la búsqueda de inmediato y sin arrastrar la página anterior", () => {
    render(<BuscadorVehiculos criterioInicial="" />);

    escribir("  AA 123  ");
    fireEvent.submit(screen.getByRole("search"));

    expect(empujar).toHaveBeenCalledExactlyOnceWith("/vehiculos?q=AA%20123");
  });

  it("limpia el criterio de la URL", () => {
    render(<BuscadorVehiculos criterioInicial="AA" />);

    fireEvent.click(screen.getByRole("button", { name: "Limpiar" }));

    expect(empujar).toHaveBeenCalledExactlyOnceWith("/vehiculos");
  });
});
