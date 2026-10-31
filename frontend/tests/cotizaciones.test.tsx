import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Cotizador } from "@/features/cotizaciones/components/cotizador";
import type { Cotizacion, TipoVehiculoCotizacion } from "@/features/cotizaciones/types";

const { calcularCotizacion } = vi.hoisted(() => ({
  calcularCotizacion: vi.fn(),
}));

vi.mock("@/features/cotizaciones/actions", () => ({
  calcularCotizacion,
}));

const tiposVehiculo: TipoVehiculoCotizacion[] = [
  {
    id: 3,
    descripcion: "Furgón grande",
    capacidad_carga_kg: "1500",
    tarifa_hora_base: "3000",
    tarifa_km_excedente: "150",
    activo: true,
    creado_en: "2026-10-01T12:00:00Z",
    actualizado_en: "2026-10-01T12:00:00Z",
  },
];

const cotizacion: Cotizacion = {
  id_tipo_vehiculo: 3,
  descripcion_tipo_vehiculo: "Furgón grande",
  horas_estimadas: "2",
  km_estimados: "15",
  tarifa_hora_base: "3000.00",
  tarifa_km_excedente: "150.00",
  base_horas: "6000.00",
  base_km: "2250.00",
  subtotal_base: "8250.00",
  requiere_ayudante: false,
  recargo_ayudante: "30000.00",
  acceso_escalera: false,
  recargo_escalera: "15000.00",
  subtotal_con_fijos: "8250.00",
  zona_concurrida: true,
  porcentaje_zona_concurrida: "15.00",
  importe_recargo_zona_concurrida: "1237.50",
  urgencia_mismo_dia: false,
  porcentaje_urgencia_mismo_dia: "20.00",
  importe_recargo_urgencia_mismo_dia: "0.00",
  total_recargos_porcentuales: "1237.50",
  precio_sugerido: "9487.50",
  moneda: "ARS",
};

describe("Cotizador", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    calcularCotizacion.mockResolvedValue({ ok: true, dato: cotizacion });
  });

  it("consulta al backend al cambiar campos y muestra su desglose", async () => {
    render(<Cotizador tiposVehiculo={tiposVehiculo} />);

    fireEvent.change(screen.getByLabelText("Tipo de vehículo"), {
      target: { value: "3" },
    });
    fireEvent.change(screen.getByLabelText("Horas estimadas"), {
      target: { value: "2" },
    });
    fireEvent.change(screen.getByLabelText("Kilómetros estimados"), {
      target: { value: "15" },
    });
    fireEvent.click(screen.getByLabelText("Zona concurrida"));

    await waitFor(() => expect(calcularCotizacion).toHaveBeenCalledOnce(), {
      timeout: 2000,
    });
    expect(calcularCotizacion).toHaveBeenCalledWith({
      id_tipo_vehiculo: 3,
      horas_estimadas: 2,
      km_estimados: 15,
      requiere_ayudante: false,
      acceso_escalera: false,
      zona_concurrida: true,
      urgencia_mismo_dia: false,
    });

    expect(
      await screen.findByText((texto) => texto.includes("9.487,50")),
    ).toBeInTheDocument();
    expect(screen.getByText("Base por horas")).toBeInTheDocument();
    expect(screen.getByText("Base por kilómetros")).toBeInTheDocument();
    expect(screen.getByText(/Recargo por zona concurrida/)).toBeInTheDocument();
  });
});
