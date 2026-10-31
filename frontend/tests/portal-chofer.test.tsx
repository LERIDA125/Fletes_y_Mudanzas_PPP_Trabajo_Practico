import { act, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { PortalChofer } from "@/features/servicios/components/portal-chofer";
import type { Servicio } from "@/features/servicios/types";

const { obtenerServiciosChofer } = vi.hoisted(() => ({
  obtenerServiciosChofer: vi.fn(),
}));

vi.mock("@/features/servicios/actions", () => ({
  obtenerServiciosChofer,
}));

vi.mock("@/features/auth/components/boton-cerrar-sesion", () => ({
  BotonCerrarSesion: () => <button type="button">Salir</button>,
}));

const fechaHoy = "2026-10-30";

function servicio(parcial: Partial<Servicio> = {}): Servicio {
  return {
    id_servicio: 41,
    id_cliente: 8,
    razon_social_cliente: "Mudanzas del Centro",
    id_tipo_vehiculo: 3,
    descripcion_tipo_vehiculo: "Furgón grande",
    id_chofer: 9,
    nombre_chofer: "Carlos Gómez",
    id_vehiculo: 12,
    patente_vehiculo: "ABC123",
    fecha: fechaHoy,
    hora_inicio: "08:30:00",
    hora_fin: null,
    horas_estimadas: "2.50",
    distancia_ida_km: "15.00",
    distancia_total_km: "30.00",
    km_franquicia: "10.00",
    km_excedente: "20.00",
    tarifa_hora_aplicada: "25000.00",
    tarifa_km_aplicada: "850.00",
    precio_total: "42000.00",
    moneda: "ARS",
    estado: "pendiente",
    transiciones_validas: ["confirmado", "cancelado"],
    motivo_cancelacion: null,
    creado_en: "2026-10-30T12:00:00Z",
    actualizado_en: "2026-10-30T12:00:00Z",
    ...parcial,
  };
}

describe("PortalChofer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("muestra viajes del día y excluye servicios de otras fechas", () => {
    render(
      <PortalChofer
        nombre="Carlos Gómez"
        fechaInicial={fechaHoy}
        serviciosIniciales={[
          servicio(),
          servicio({
            id_servicio: 42,
            fecha: "2026-10-31",
            razon_social_cliente: "Viaje de mañana",
          }),
        ]}
        errorInicial={null}
      />,
    );

    expect(screen.getByRole("heading", { name: "Hola, Carlos Gómez" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Tus viajes de hoy" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Mudanzas del Centro" })).toBeVisible();
    expect(screen.queryByText("Viaje de mañana")).not.toBeInTheDocument();
    expect(screen.getByText("08:30")).toBeVisible();
    expect(screen.getByText(/ABC123/)).toBeVisible();
  });

  it("muestra una agenda vacía cuando no hay servicios para hoy", () => {
    render(
      <PortalChofer
        nombre="Carlos"
        fechaInicial={fechaHoy}
        serviciosIniciales={[]}
        errorInicial={null}
      />,
    );

    expect(screen.getByText("Hoy no tenés viajes asignados")).toBeVisible();
    expect(screen.getByText("0 viajes")).toBeVisible();
  });

  it("actualiza los servicios cada diez segundos", async () => {
    vi.useFakeTimers();
    obtenerServiciosChofer.mockResolvedValue({
      ok: true,
      dato: [servicio({ razon_social_cliente: "Servicio actualizado" })],
    });

    render(
      <PortalChofer
        nombre="Carlos"
        fechaInicial={fechaHoy}
        serviciosIniciales={[]}
        errorInicial={null}
      />,
    );

    await act(async () => {
      await vi.advanceTimersByTimeAsync(20_000);
    });

    expect(obtenerServiciosChofer).toHaveBeenCalledTimes(2);
    expect(screen.getByRole("heading", { name: "Servicio actualizado" })).toBeVisible();
  });
});
