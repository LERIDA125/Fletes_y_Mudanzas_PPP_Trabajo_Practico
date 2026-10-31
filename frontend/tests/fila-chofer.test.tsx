import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { FilaChofer } from "@/features/choferes/components/fila-chofer";

import type { Chofer } from "@/features/choferes/types";

const { guardarChofer, eliminarChofer, refresh } = vi.hoisted(() => ({
  guardarChofer: vi.fn(),
  eliminarChofer: vi.fn(),
  refresh: vi.fn(),
}));

vi.mock("@/features/choferes/actions", () => ({
  guardarChofer,
  eliminarChofer,
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

function choferDePrueba(sobrescritura: Partial<Chofer> = {}): Chofer {
  return {
    id: 7,
    nombre_completo: "Juan Pérez",
    telefono: "351 555 0100",
    activo: true,
    saldo_a_favor: 1500,
    creado_en: "2026-03-12T12:00:00Z",
    actualizado_en: "2026-03-12T12:00:00Z",
    ...sobrescritura,
  };
}

function renderizarFila(chofer = choferDePrueba()) {
  return render(
    <table>
      <tbody>
        <FilaChofer chofer={chofer} />
      </tbody>
    </table>,
  );
}

describe("FilaChofer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    guardarChofer.mockResolvedValue({ ok: true, dato: choferDePrueba() });
    eliminarChofer.mockResolvedValue({ ok: true });
  });

  it("abre el menú de acciones con Editar y Dar de baja", async () => {
    const usuario = userEvent.setup();
    renderizarFila();

    await usuario.click(screen.getByRole("button", { name: "Opciones de Juan Pérez" }));

    expect(screen.getByRole("button", { name: "Editar" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Dar de baja" })).toBeInTheDocument();
  });

  it("abre el modal precargado y guarda los cambios", async () => {
    const usuario = userEvent.setup();
    renderizarFila();

    await usuario.click(screen.getByRole("button", { name: "Opciones de Juan Pérez" }));
    await usuario.click(screen.getByRole("button", { name: "Editar" }));

    expect(await screen.findByRole("dialog")).toBeInTheDocument();
    expect(screen.getByLabelText("Nombre completo")).toHaveValue("Juan Pérez");
    expect(screen.getByLabelText("Teléfono")).toHaveValue("351 555 0100");

    await usuario.clear(screen.getByLabelText("Teléfono"));
    await usuario.type(screen.getByLabelText("Teléfono"), "351 555 0199");
    await usuario.click(screen.getByRole("button", { name: "Guardar cambios" }));

    await waitFor(() => {
      expect(guardarChofer).toHaveBeenCalledWith(
        { nombre_completo: "Juan Pérez", telefono: "351 555 0199" },
        7,
      );
      expect(refresh).toHaveBeenCalledOnce();
    });
  });

  it("pide confirmación antes de dar de baja el chofer", async () => {
    const usuario = userEvent.setup();
    renderizarFila();

    await usuario.click(screen.getByRole("button", { name: "Opciones de Juan Pérez" }));
    await usuario.click(screen.getByRole("button", { name: "Dar de baja" }));

    expect(await screen.findByRole("dialog")).toHaveTextContent(
      "¿Dar de baja a Juan Pérez? Esta acción no se puede deshacer.",
    );
    expect(eliminarChofer).not.toHaveBeenCalled();
    expect(refresh).not.toHaveBeenCalled();

    await usuario.click(screen.getByRole("button", { name: "Sí, dar de baja" }));

    await waitFor(() => {
      expect(eliminarChofer).toHaveBeenCalledWith(7);
      expect(refresh).toHaveBeenCalledOnce();
    });
  });

  it("muestra el error del backend al intentar dar de baja", async () => {
    const usuario = userEvent.setup();
    eliminarChofer.mockResolvedValue({
      ok: false,
      mensaje: "El chofer ya no existe o fue dado de baja. Actualizá el listado.",
    });
    renderizarFila();

    await usuario.click(screen.getByRole("button", { name: "Opciones de Juan Pérez" }));
    await usuario.click(screen.getByRole("button", { name: "Dar de baja" }));
    await usuario.click(screen.getByRole("button", { name: "Sí, dar de baja" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "El chofer ya no existe o fue dado de baja. Actualizá el listado.",
    );
    expect(refresh).not.toHaveBeenCalled();
  });
});
