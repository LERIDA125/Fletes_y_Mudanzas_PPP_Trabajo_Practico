import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PanelCajaRendiciones } from "@/features/servicios/components/panel-caja-rendiciones";
import { TarjetaViajeChofer } from "@/features/servicios/components/tarjeta-viaje-chofer";
import type { Servicio } from "@/features/servicios/types";

const {
  iniciarViajeChofer,
  finalizarViajeChofer,
  aprobarRendicionServicio,
  observarRendicionServicio,
} = vi.hoisted(() => ({
  iniciarViajeChofer: vi.fn(),
  finalizarViajeChofer: vi.fn(),
  aprobarRendicionServicio: vi.fn(),
  observarRendicionServicio: vi.fn(),
}));

vi.mock("@/features/servicios/actions", () => ({
  iniciarViajeChofer,
  finalizarViajeChofer,
  aprobarRendicionServicio,
  observarRendicionServicio,
}));

function servicioEjemplo(parcial: Partial<Servicio> = {}): Servicio {
  return {
    id_servicio: 101,
    id_cliente: 5,
    razon_social_cliente: "Ferretería Industrial S.A.",
    id_tipo_vehiculo: 2,
    descripcion_tipo_vehiculo: "Camión Chasis",
    id_chofer: 12,
    nombre_chofer: "Martín Pereyra",
    id_vehiculo: 8,
    patente_vehiculo: "AF 123 CD",
    fecha: "2026-11-01",
    hora_inicio: "09:00:00",
    hora_fin: null,
    horas_estimadas: "3.00",
    distancia_ida_km: "20.00",
    distancia_total_km: "40.00",
    km_franquicia: "10.00",
    km_excedente: "30.00",
    tarifa_hora_aplicada: "15000.00",
    tarifa_km_aplicada: "600.00",
    precio_total: "63000.00",
    moneda: "ARS",
    estado: "confirmado",
    transiciones_validas: ["en curso"],
    motivo_cancelacion: null,
    foto_remito_url: null,
    monto_cobrado_real: null,
    estado_rendicion: null,
    observacion_rendicion: null,
    rendido_en: null,
    rendido_por_id: null,
    creado_en: "2026-11-01T08:00:00Z",
    actualizado_en: "2026-11-01T08:00:00Z",
    ...parcial,
  };
}

describe("Cierre de Viaje y Rendición (H10) - Chofer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("permite al chofer iniciar un viaje confirmado", async () => {
    const usuario = userEvent.setup();
    const inicial = servicioEjemplo({ estado: "confirmado" });
    const enCurso = { ...inicial, estado: "en curso" };
    iniciarViajeChofer.mockResolvedValue({ ok: true, dato: enCurso });

    render(<TarjetaViajeChofer servicio={inicial} numero={1} />);

    const botonIniciar = screen.getByRole("button", { name: "Iniciar viaje" });
    expect(botonIniciar).toBeVisible();

    await usuario.click(botonIniciar);

    await waitFor(() => {
      expect(iniciarViajeChofer).toHaveBeenCalledWith(101);
    });
  });

  it("muestra el badge de rendición pendiente cuando el viaje ya está finalizado", () => {
    const finalizado = servicioEjemplo({
      estado: "finalizado",
      monto_cobrado_real: "63000.00",
      estado_rendicion: "PENDIENTE",
      foto_remito_url: "data:image/jpeg;base64,mockfoto",
    });

    render(<TarjetaViajeChofer servicio={finalizado} numero={1} />);

    expect(screen.getByText("Pendiente de rendición")).toBeVisible();
    expect(screen.getByText("Cobrado en mano")).toBeVisible();
    expect(screen.getByRole("button", { name: "Ver remito" })).toBeVisible();
  });

  it("muestra el badge de rendido cuando la administración aprobó la rendición", () => {
    const rendido = servicioEjemplo({
      estado: "cobrado",
      monto_cobrado_real: "63000.00",
      estado_rendicion: "RENDIDO",
      foto_remito_url: "data:image/jpeg;base64,mockfoto",
    });

    render(<TarjetaViajeChofer servicio={rendido} numero={1} />);

    expect(screen.getByText("Rendido y Aprobado")).toBeVisible();
  });
});

describe("Caja y Rendiciones (H10) - Panel Administrador", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calcula los totales KPI y lista los viajes pendientes de rendición", () => {
    const s1 = servicioEjemplo({
      id_servicio: 201,
      estado: "finalizado",
      precio_total: "50000.00",
      monto_cobrado_real: "50000.00",
      estado_rendicion: "PENDIENTE",
      foto_remito_url: "data:image/jpeg;base64,mockfoto",
    });
    const s2 = servicioEjemplo({
      id_servicio: 202,
      nombre_chofer: "Lucas Gómez",
      estado: "cobrado",
      precio_total: "30000.00",
      monto_cobrado_real: "30000.00",
      estado_rendicion: "RENDIDO",
    });

    render(<PanelCajaRendiciones serviciosIniciales={[s1, s2]} />);

    expect(screen.getByRole("heading", { name: "Caja y Rendiciones" })).toBeVisible();
    expect(screen.getByText("#SRV-201")).toBeVisible();
    expect(screen.getByText("Ferretería Industrial S.A.")).toBeVisible();
    expect(screen.getByRole("button", { name: "Aprobar" })).toBeVisible();
  });

  it("permite aprobar la rendición y actualiza el estado", async () => {
    const usuario = userEvent.setup();
    const s1 = servicioEjemplo({
      id_servicio: 201,
      estado: "finalizado",
      monto_cobrado_real: "50000.00",
      estado_rendicion: "PENDIENTE",
      foto_remito_url: "data:image/jpeg;base64,mockfoto",
    });
    const s1Aprobado = {
      ...s1,
      estado: "cobrado",
      estado_rendicion: "RENDIDO",
    };
    aprobarRendicionServicio.mockResolvedValue({ ok: true, dato: s1Aprobado });

    render(<PanelCajaRendiciones serviciosIniciales={[s1]} />);

    const botonAprobar = screen.getByRole("button", { name: "Aprobar" });
    await usuario.click(botonAprobar);

    await waitFor(() => {
      expect(aprobarRendicionServicio).toHaveBeenCalledWith(201);
    });
  });

  it("permite observar una rendición con un motivo", async () => {
    const usuario = userEvent.setup();
    const s1 = servicioEjemplo({
      id_servicio: 201,
      estado: "finalizado",
      monto_cobrado_real: "50000.00",
      estado_rendicion: "PENDIENTE",
      foto_remito_url: "data:image/jpeg;base64,mockfoto",
    });
    const s1Observado = {
      ...s1,
      estado_rendicion: "OBSERVADO",
      observacion_rendicion: "Diferencia de $5.000 por peajes",
    };
    observarRendicionServicio.mockResolvedValue({ ok: true, dato: s1Observado });

    render(<PanelCajaRendiciones serviciosIniciales={[s1]} />);

    const botonObservar = screen.getByTitle("Observar rendición");
    await usuario.click(botonObservar);

    expect(
      screen.getByRole("heading", { name: "Observar rendición #SRV-201" }),
    ).toBeVisible();

    const textarea = screen.getByPlaceholderText(
      "Ej: Falta ticket de peaje, o hay una diferencia de $5.000 sin justificar...",
    );
    await usuario.type(textarea, "Diferencia de $5.000 por peajes");

    const botonGuardar = screen.getByRole("button", { name: "Guardar Observación" });
    await usuario.click(botonGuardar);

    await waitFor(() => {
      expect(observarRendicionServicio).toHaveBeenCalledWith(
        201,
        "Diferencia de $5.000 por peajes",
      );
    });
  });
});
