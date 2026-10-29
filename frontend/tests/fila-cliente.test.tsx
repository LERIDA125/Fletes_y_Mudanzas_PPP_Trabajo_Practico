import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { FilaCliente } from "@/features/clientes/components/fila-cliente";
import { NuevoCliente } from "@/features/clientes/components/nuevo-cliente";

import type { Cliente } from "@/features/clientes/types";

const { guardarCliente, eliminarCliente, refresh } = vi.hoisted(() => ({
  guardarCliente: vi.fn(),
  eliminarCliente: vi.fn(),
  refresh: vi.fn(),
}));

vi.mock("@/features/clientes/actions", () => ({
  guardarCliente,
  eliminarCliente,
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

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

function renderizarFila(cliente = clienteDePrueba()) {
  return render(
    <table>
      <tbody>
        <FilaCliente cliente={cliente} />
      </tbody>
    </table>,
  );
}

describe("FilaCliente", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    guardarCliente.mockResolvedValue({ ok: true, dato: clienteDePrueba() });
    eliminarCliente.mockResolvedValue({ ok: true, dato: undefined });
  });

  it("muestra los cuatro datos del listado (FR-011)", () => {
    renderizarFila();

    expect(screen.getByText("Distribuidora del Sur")).toBeInTheDocument();
    expect(screen.getByText("Av. Rivadavia 5400")).toBeInTheDocument();
    expect(screen.getByText("+54 11 5555-4321")).toBeInTheDocument();
    expect(screen.getByText("Sí")).toBeInTheDocument();
    expect(screen.getByText("12/03/2026")).toBeInTheDocument();
  });

  it("dice «No» cuando el cliente no tiene cuenta corriente", () => {
    renderizarFila(clienteDePrueba({ tiene_cuenta_corriente: false }));

    expect(screen.getByText("No")).toBeInTheDocument();
    expect(screen.queryByText("Sí")).toBeNull();
  });

  it("usa la razón social como encabezado de fila, no la dirección", () => {
    renderizarFila();

    const encabezado = screen.getByRole("rowheader");
    expect(encabezado).toHaveTextContent("Distribuidora del Sur");
    expect(encabezado).not.toHaveAttribute("scope", "col");
  });

  it("abre el menú de acciones con Editar y Dar de baja", async () => {
    const usuario = userEvent.setup();
    renderizarFila();

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Distribuidora del Sur" }),
    );

    expect(screen.getByRole("button", { name: "Editar" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Dar de baja" })).toBeInTheDocument();
  });

  it("abre el modal precargado y guarda los cambios (FR-012)", async () => {
    const usuario = userEvent.setup();
    renderizarFila();

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Distribuidora del Sur" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Editar" }));

    expect(await screen.findByRole("dialog")).toBeInTheDocument();
    expect(screen.getByLabelText("Razón social")).toHaveValue("Distribuidora del Sur");
    expect(screen.getByLabelText("Teléfono")).toHaveValue("+54 11 5555-4321");
    expect(screen.getByLabelText("Dirección habitual")).toHaveValue("Av. Rivadavia 5400");
    expect(screen.getByLabelText("Tiene cuenta corriente")).toBeChecked();

    await usuario.clear(screen.getByLabelText("Teléfono"));
    await usuario.type(screen.getByLabelText("Teléfono"), "11 5555-0000");
    await usuario.click(screen.getByRole("button", { name: "Guardar cambios" }));

    await waitFor(() => {
      expect(guardarCliente).toHaveBeenCalledWith(
        {
          razon_social: "Distribuidora del Sur",
          telefono: "11 5555-0000",
          direccion_habitual: "Av. Rivadavia 5400",
          tiene_cuenta_corriente: true,
        },
        1,
      );
      expect(refresh).toHaveBeenCalledOnce();
    });
  });

  it("permite dar de alta un nuevo cliente desde NuevoCliente", async () => {
    const usuario = userEvent.setup();
    render(<NuevoCliente />);

    await usuario.click(screen.getByRole("button", { name: /Nuevo cliente/i }));

    expect(await screen.findByRole("dialog")).toBeInTheDocument();
    await usuario.type(screen.getByLabelText("Razón social"), "Mueblería Belgrano");
    await usuario.type(screen.getByLabelText("Teléfono"), "11 4444-8888");
    await usuario.type(screen.getByLabelText("Dirección habitual"), "Av. Cabildo 2100");
    await usuario.click(screen.getByLabelText("Tiene cuenta corriente"));
    await usuario.click(screen.getByRole("button", { name: "Guardar cliente" }));

    await waitFor(() => {
      expect(guardarCliente).toHaveBeenCalledWith(
        {
          razon_social: "Mueblería Belgrano",
          telefono: "11 4444-8888",
          direccion_habitual: "Av. Cabildo 2100",
          tiene_cuenta_corriente: true,
        },
        undefined,
      );
      expect(refresh).toHaveBeenCalledOnce();
    });
  });

  it("muestra en el formulario el error del backend al modificar", async () => {
    const usuario = userEvent.setup();
    guardarCliente.mockResolvedValue({
      ok: false,
      mensaje: "Ya existe un cliente con la razón social 'distribuidora del sur'",
    });
    renderizarFila();

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Distribuidora del Sur" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Editar" }));
    await usuario.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Ya existe un cliente con la razón social 'distribuidora del sur'",
    );
    expect(refresh).not.toHaveBeenCalled();
  });

  it("pide confirmación antes de dar de baja al cliente", async () => {
    const usuario = userEvent.setup();
    renderizarFila();

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Distribuidora del Sur" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Dar de baja" }));

    expect(await screen.findByRole("dialog")).toHaveTextContent(
      "¿Dar de baja a Distribuidora del Sur? Esta acción no se puede deshacer.",
    );
    expect(eliminarCliente).not.toHaveBeenCalled();
    expect(refresh).not.toHaveBeenCalled();

    await usuario.click(screen.getByRole("button", { name: "Sí, dar de baja" }));

    await waitFor(() => {
      expect(eliminarCliente).toHaveBeenCalledWith(1);
      expect(refresh).toHaveBeenCalledOnce();
    });
  });

  it("permite cancelar la baja desde el diálogo sin llamar a la API", async () => {
    const usuario = userEvent.setup();
    renderizarFila();

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Distribuidora del Sur" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Dar de baja" }));
    await usuario.click(screen.getByRole("button", { name: "Cancelar" }));

    expect(eliminarCliente).not.toHaveBeenCalled();
  });

  it("explica que no se puede dar de baja un cliente con servicios (FR-015)", async () => {
    const usuario = userEvent.setup();
    eliminarCliente.mockResolvedValue({
      ok: false,
      mensaje: "No se puede dar de baja un cliente que tiene servicios registrados.",
    });
    renderizarFila();

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Distribuidora del Sur" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Dar de baja" }));
    await usuario.click(screen.getByRole("button", { name: "Sí, dar de baja" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "No se puede dar de baja un cliente que tiene servicios registrados.",
    );
    expect(refresh).not.toHaveBeenCalled();
  });
});
