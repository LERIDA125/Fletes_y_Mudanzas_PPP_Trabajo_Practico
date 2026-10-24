import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { FilaVehiculo } from "@/features/vehiculos/components/fila-vehiculo";
import { ListadoVehiculos } from "@/features/vehiculos/components/listado-vehiculos";
import { EstadoError } from "@/features/vehiculos/components/estados/error";
import { EstadoVacio } from "@/features/vehiculos/components/estados/vacio";

import type { Vehiculo } from "@/features/vehiculos/types";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: vi.fn() }),
}));

vi.mock("@/features/vehiculos/actions", () => ({
  guardarVehiculo: vi.fn(),
  guardarTarifasTipo: vi.fn(),
  obtenerCatalogosVehiculo: vi.fn(),
}));

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

describe("ListadoVehiculos", () => {
  it("muestra datos legibles de las relaciones y la capacidad", () => {
    render(<ListadoVehiculos vehiculos={[vehiculoDePrueba()]} />);

    expect(
      screen.getByRole("table", { name: "Vehículos activos de la empresa" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("rowheader")).toHaveTextContent("AA 123 ABC");
    expect(screen.getByText("Camioneta mediana")).toBeInTheDocument();
    expect(screen.getByText("1.500 kg")).toBeInTheDocument();
    expect(screen.getByText("Juan Pérez")).toBeInTheDocument();
    expect(screen.getByText("12/03/2026")).toBeInTheDocument();
  });

  it("indica cuando no hay un chofer habitual asignado", () => {
    render(
      <table>
        <tbody>
          <FilaVehiculo
            vehiculo={vehiculoDePrueba({
              id_chofer_habitual: null,
              nombre_chofer_habitual: null,
            })}
          />
        </tbody>
      </table>,
    );

    expect(
      screen.getByText("Sin chofer habitual", { selector: "td" }),
    ).toBeInTheDocument();
  });
});

describe("Estados del listado de vehículos", () => {
  it("distingue una búsqueda sin coincidencias y permite limpiarla", () => {
    render(<EstadoVacio criterio="ZZ 999" rutaSinBusqueda="/vehiculos" />);

    expect(screen.getByRole("status")).toHaveTextContent(
      "No hay vehículos cuya patente contenga «ZZ 999».",
    );
    expect(screen.getByRole("link", { name: "Limpiar búsqueda" })).toHaveAttribute(
      "href",
      "/vehiculos",
    );
  });

  it("presenta un error comprensible y la acción para reintentar", () => {
    render(<EstadoError clase="sin-respuesta" />);

    expect(screen.getByRole("alert")).toHaveTextContent(
      "No pudimos conectar con el sistema.",
    );
    expect(screen.getByRole("button", { name: "Reintentar" })).toBeInTheDocument();
  });
});
