import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { FilaVehiculo } from "@/features/vehiculos/components/fila-vehiculo";

import type { TipoVehiculo, Vehiculo } from "@/features/vehiculos/types";

const { guardarVehiculo, eliminarVehiculo, refresh } = vi.hoisted(() => ({
  guardarVehiculo: vi.fn(),
  eliminarVehiculo: vi.fn(),
  refresh: vi.fn(),
}));

vi.mock("@/features/vehiculos/actions", () => ({
  guardarVehiculo,
  eliminarVehiculo,
  obtenerCatalogosVehiculo: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

const tipoDePrueba: TipoVehiculo = {
  id: 1,
  descripcion: "Camioneta mediana",
  capacidad_carga_kg: "1500.00",
  tarifa_hora_base: "10000.00",
  tarifa_km_excedente: "500.00",
  activo: true,
  creado_en: "2026-03-12T12:00:00Z",
  actualizado_en: "2026-03-12T12:00:00Z",
};

function vehiculoDePrueba(sobrescritura: Partial<Vehiculo> = {}): Vehiculo {
  return {
    id: 1,
    patente: "AA 123 ABC",
    id_tipo_vehiculo: 1,
    id_chofer_habitual: 2,
    activo: true,
    creado_en: "2026-03-12T12:00:00Z",
    actualizado_en: "2026-03-12T12:00:00Z",
    descripcion_tipo_vehiculo: "Camioneta mediana",
    capacidad_carga_kg: 1500,
    nombre_chofer_habitual: "Juan Pérez",
    ...sobrescritura,
  };
}

function renderizarFila(vehiculo = vehiculoDePrueba()) {
  return render(
    <table>
      <tbody>
        <FilaVehiculo vehiculo={vehiculo} tiposVehiculo={[tipoDePrueba]} choferes={[]} />
      </tbody>
    </table>,
  );
}

describe("FilaVehiculo", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    guardarVehiculo.mockResolvedValue({ ok: true, dato: vehiculoDePrueba() });
    eliminarVehiculo.mockResolvedValue({ ok: true });
  });

  it("abre el menú de acciones con Editar y Dar de baja", async () => {
    const usuario = userEvent.setup();
    renderizarFila();

    await usuario.click(screen.getByRole("button", { name: "Opciones de AA 123 ABC" }));

    expect(screen.getByRole("button", { name: "Editar" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Dar de baja" })).toBeInTheDocument();
  });

  it("abre el modal precargado y guarda los cambios", async () => {
    const usuario = userEvent.setup();
    renderizarFila();

    await usuario.click(screen.getByRole("button", { name: "Opciones de AA 123 ABC" }));
    await usuario.click(screen.getByRole("button", { name: "Editar" }));

    expect(await screen.findByRole("dialog")).toBeInTheDocument();
    expect(screen.getByLabelText("Patente")).toHaveValue("AA 123 ABC");
    expect(screen.getByLabelText("Tipo de vehículo")).toHaveValue("1");

    await usuario.clear(screen.getByLabelText("Patente"));
    await usuario.type(screen.getByLabelText("Patente"), "AB 456 CDE");
    await usuario.click(screen.getByRole("button", { name: "Guardar cambios" }));

    await waitFor(() => {
      expect(guardarVehiculo).toHaveBeenCalledWith(
        {
          patente: "AB 456 CDE",
          id_tipo_vehiculo: 1,
          id_chofer_habitual: 2,
        },
        1,
      );
      expect(refresh).toHaveBeenCalledOnce();
    });
  });

  it("pide confirmación antes de dar de baja el vehículo", async () => {
    const usuario = userEvent.setup();
    const confirmacion = vi.spyOn(window, "confirm").mockReturnValue(false);
    renderizarFila();

    await usuario.click(screen.getByRole("button", { name: "Opciones de AA 123 ABC" }));
    await usuario.click(screen.getByRole("button", { name: "Dar de baja" }));

    expect(confirmacion).toHaveBeenCalledWith(
      "¿Dar de baja el vehículo AA 123 ABC? Esta acción no se puede deshacer.",
    );
    expect(eliminarVehiculo).not.toHaveBeenCalled();
    expect(refresh).not.toHaveBeenCalled();

    confirmacion.mockReturnValue(true);
    await usuario.click(screen.getByRole("button", { name: "Dar de baja" }));

    await waitFor(() => {
      expect(eliminarVehiculo).toHaveBeenCalledWith(1);
      expect(refresh).toHaveBeenCalledOnce();
    });
    confirmacion.mockRestore();
  });

  it("explica que no se puede dar de baja un vehículo con servicios", async () => {
    const usuario = userEvent.setup();
    vi.spyOn(window, "confirm").mockReturnValue(true);
    eliminarVehiculo.mockResolvedValue({
      ok: false,
      mensaje: "No se puede dar de baja un vehículo que tiene servicios registrados.",
    });
    renderizarFila();

    await usuario.click(screen.getByRole("button", { name: "Opciones de AA 123 ABC" }));
    await usuario.click(screen.getByRole("button", { name: "Dar de baja" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "No se puede dar de baja un vehículo que tiene servicios registrados.",
    );
    expect(refresh).not.toHaveBeenCalled();
  });
});
