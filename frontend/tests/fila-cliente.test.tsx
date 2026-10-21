import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { FilaCliente } from "@/features/clientes/components/fila-cliente";

import type { Cliente } from "@/features/clientes/types";

function clienteDePrueba(sobrescritura: Partial<Cliente> = {}): Cliente {
  return {
    id: 1,
    razon_social: "Distribuidora del Sur",
    telefono: "+54 11 5555-4321",
    direccion_habitual: "Av. Rivadavia 5400",
    tiene_cuenta_corriente: true,
    activo: true,
    creado_en: "2026-03-12T12:00:00Z",
    actualizado_en: "2026-03-12T12:00:00Z",
    ...sobrescritura,
  };
}

describe("FilaCliente", () => {
  it("muestra los cuatro datos del listado (FR-011)", () => {
    render(
      <table>
        <tbody>
          <FilaCliente cliente={clienteDePrueba()} />
        </tbody>
      </table>,
    );

    expect(screen.getByText("Distribuidora del Sur")).toBeInTheDocument();
    expect(screen.getByText("Av. Rivadavia 5400")).toBeInTheDocument();
    expect(screen.getByText("+54 11 5555-4321")).toBeInTheDocument();
    expect(screen.getByText("Sí")).toBeInTheDocument();
    expect(screen.getByText("12/03/2026")).toBeInTheDocument();
  });

  it("dice «No» cuando el cliente no tiene cuenta corriente", () => {
    render(
      <table>
        <tbody>
          <FilaCliente cliente={clienteDePrueba({ tiene_cuenta_corriente: false })} />
        </tbody>
      </table>,
    );

    expect(screen.getByText("No")).toBeInTheDocument();
    expect(screen.queryByText("Sí")).toBeNull();
  });

  it("usa la razón social como encabezado de fila, no la dirección", () => {
    render(
      <table>
        <tbody>
          <FilaCliente cliente={clienteDePrueba()} />
        </tbody>
      </table>,
    );

    const encabezado = screen.getByRole("rowheader");
    expect(encabezado).toHaveTextContent("Distribuidora del Sur");
    expect(encabezado).not.toHaveAttribute("scope", "col");
  });
});
