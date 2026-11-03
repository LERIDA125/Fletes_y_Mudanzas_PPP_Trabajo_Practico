import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { DialogoRendicion } from "@/features/rendiciones/components/dialogo-rendicion";
import { TablaRendiciones } from "@/features/rendiciones/components/tabla-rendiciones";
import type { Rendicion, ServicioElegible } from "@/features/rendiciones/types";

const { guardarRendicion, cambiarEstado, refresh } = vi.hoisted(() => ({
  guardarRendicion: vi.fn(),
  cambiarEstado: vi.fn(),
  refresh: vi.fn(),
}));

vi.mock("@/features/rendiciones/actions", () => ({
  guardarRendicion,
  cambiarEstado,
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

function rendicionDePrueba(sobrescritura: Partial<Rendicion> = {}): Rendicion {
  return {
    id: 1,
    codigo: "REN-001",
    id_servicio: 10,
    id_chofer: 3,
    nombre_chofer: "Carlos Méndez",
    razon_social_cliente: "María González",
    fecha: "2026-11-03",
    tarifa: "18500.00",
    adelanto: "12000.00",
    gastos_informados: {
      combustible: "2000.00",
      peajes: "300.00",
      otros: "200.00",
    },
    gastos_total: "2500.00",
    saldo: "4000.00",
    moneda: "ARS",
    estado: "pendiente",
    observaciones: "Comprobantes entregados",
    creado_por_id: 1,
    modificado_por_id: 1,
    creado_en: "2026-11-03T12:00:00Z",
    actualizado_en: "2026-11-03T12:00:00Z",
    ...sobrescritura,
  };
}

function servicioElegible(
  sobrescritura: Partial<ServicioElegible> = {},
): ServicioElegible {
  return {
    id_servicio: 10,
    razon_social_cliente: "María González",
    nombre_chofer: "Carlos Méndez",
    fecha: "2026-11-03",
    hora_inicio: "08:30:00",
    precio_total: "18500.00",
    ...sobrescritura,
  };
}

describe("TablaRendiciones", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    cambiarEstado.mockResolvedValue({ ok: true, dato: rendicionDePrueba() });
  });

  it("muestra la rendición con importes y estado formateados", () => {
    render(
      <TablaRendiciones rendiciones={[rendicionDePrueba({ estado: "en revision" })]} />,
    );

    expect(screen.getByText("REN-001")).toBeInTheDocument();
    expect(screen.getByText("Carlos Méndez")).toBeInTheDocument();
    expect(screen.getByText("María González")).toBeInTheDocument();
    expect(screen.getByText("03/11/2026")).toBeInTheDocument();
    expect(screen.getByText("En revisión")).toBeInTheDocument();
    expect(screen.getAllByText(/18\.500,00/).length).toBeGreaterThan(0);
  });

  it("abre el detalle con el desglose de gastos y aprueba la rendición", async () => {
    const usuario = userEvent.setup();
    render(<TablaRendiciones rendiciones={[rendicionDePrueba()]} />);

    await usuario.click(screen.getByRole("button", { name: "Ver detalle" }));

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Combustible")).toBeInTheDocument();
    expect(screen.getAllByText(/2\.500,00/).length).toBeGreaterThan(0);
    expect(screen.getByText("Comprobantes entregados")).toBeInTheDocument();

    await usuario.click(screen.getByRole("button", { name: "Aprobar rendición" }));

    await waitFor(() => {
      expect(cambiarEstado).toHaveBeenCalledWith(1, "aprobada");
      expect(refresh).toHaveBeenCalled();
    });
  });

  it("no ofrece aprobar una rendición ya aprobada", async () => {
    const usuario = userEvent.setup();
    render(
      <TablaRendiciones rendiciones={[rendicionDePrueba({ estado: "aprobada" })]} />,
    );

    await usuario.click(screen.getByRole("button", { name: "Ver detalle" }));

    expect(screen.queryByRole("button", { name: "Aprobar rendición" })).toBeNull();
  });
});

describe("DialogoRendicion", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    guardarRendicion.mockResolvedValue({ ok: true, dato: rendicionDePrueba() });
  });

  it("toma la tarifa del servicio elegido y la actualiza al cambiarlo", async () => {
    const usuario = userEvent.setup();
    render(
      <DialogoRendicion
        servicios={[
          servicioElegible(),
          servicioElegible({
            id_servicio: 11,
            precio_total: "22000.00",
            razon_social_cliente: "Estudio Norte",
            nombre_chofer: "Lucía Fernández",
          }),
        ]}
        onCerrar={vi.fn()}
      />,
    );

    expect(screen.getByLabelText("Tarifa acordada")).toHaveValue(18500);

    await usuario.selectOptions(screen.getByLabelText("Servicio finalizado"), "11");

    expect(screen.getByLabelText("Tarifa acordada")).toHaveValue(22000);
  });

  it("envía los gastos informados y cierra el modal al guardar", async () => {
    const usuario = userEvent.setup();
    const cerrar = vi.fn();
    render(<DialogoRendicion servicios={[servicioElegible()]} onCerrar={cerrar} />);

    await usuario.clear(screen.getByLabelText("Adelanto previo"));
    await usuario.type(screen.getByLabelText("Adelanto previo"), "12000");
    await usuario.type(screen.getByLabelText("Combustible"), "2000");
    await usuario.type(screen.getByLabelText("Peajes"), "300");
    await usuario.type(screen.getByLabelText("Otros"), "200");
    await usuario.type(
      screen.getByLabelText("Observaciones (opcional)"),
      "Comprobantes entregados",
    );
    await usuario.click(screen.getByRole("button", { name: "Guardar rendición" }));

    await waitFor(() => {
      expect(guardarRendicion).toHaveBeenCalledWith({
        id_servicio: 10,
        tarifa: 18500,
        adelanto: 12000,
        gastos_informados: { combustible: 2000, peajes: 300, otros: 200 },
        observaciones: "Comprobantes entregados",
      });
      expect(cerrar).toHaveBeenCalled();
      expect(refresh).toHaveBeenCalled();
    });
  });

  it("muestra el error del backend sin cerrar el modal", async () => {
    guardarRendicion.mockResolvedValue({
      ok: false,
      mensaje: "El servicio ya tiene una rendición registrada.",
    });
    const usuario = userEvent.setup();
    const cerrar = vi.fn();
    render(<DialogoRendicion servicios={[servicioElegible()]} onCerrar={cerrar} />);

    await usuario.click(screen.getByRole("button", { name: "Guardar rendición" }));

    expect(
      await screen.findByText("El servicio ya tiene una rendición registrada."),
    ).toBeInTheDocument();
    expect(cerrar).not.toHaveBeenCalled();
  });

  it("bloquea el alta cuando no hay servicios elegibles", () => {
    render(<DialogoRendicion servicios={[]} onCerrar={vi.fn()} />);

    expect(
      screen.getByText(/No hay servicios finalizados con chofer sin rendición/),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Guardar rendición" })).toBeDisabled();
  });
});
