import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ModalFinalizarViaje } from "@/features/servicios/components/modal-finalizar-viaje";
import { PanelCajaRendiciones } from "@/features/servicios/components/panel-caja-rendiciones";
import type { Servicio } from "@/features/servicios/types";

const { aprobarRendicionAccion, observarRendicionAccion, finalizarViajeChofer } =
  vi.hoisted(() => ({
    aprobarRendicionAccion: vi.fn(),
    observarRendicionAccion: vi.fn(),
    finalizarViajeChofer: vi.fn(),
  }));

vi.mock("@/features/servicios/actions", () => ({
  aprobarRendicionAccion,
  observarRendicionAccion,
  finalizarViajeChofer,
}));

function crearServicioTest(parcial: Partial<Servicio> = {}): Servicio {
  return {
    id_servicio: 101,
    id_cliente: 5,
    razon_social_cliente: "Ferretería Central",
    id_tipo_vehiculo: 1,
    descripcion_tipo_vehiculo: "Camioneta Mediana",
    id_chofer: 10,
    nombre_chofer: "Marcelo Rodriguez",
    id_vehiculo: 2,
    patente_vehiculo: "AA123BB",
    fecha: "2026-11-02",
    hora_inicio: "09:00:00",
    hora_fin: "11:30:00",
    horas_estimadas: "2.50",
    distancia_ida_km: "12.00",
    origen_direccion: null,
    destino_direccion: null,
    distancia_total_km: "24.00",
    km_franquicia: "10.00",
    km_excedente: "14.00",
    tarifa_hora_aplicada: "18000.00",
    tarifa_km_aplicada: "650.00",
    requiere_ayudante: false,
    acceso_escalera: false,
    zona_concurrida: false,
    urgencia_mismo_dia: false,
    recargo_ayudante_aplicado: "0.00",
    recargo_escalera_aplicado: "0.00",
    importe_recargo_zona_aplicado: "0.00",
    importe_recargo_urgencia_aplicado: "0.00",
    porcentaje_zona_aplicado: "0.00",
    porcentaje_urgencia_aplicado: "0.00",
    precio_sugerido: "54100.00",
    precio_acordado: "54100.00",
    precio_total: "54100.00",
    moneda: "ARS",
    estado: "finalizado",
    transiciones_validas: ["cobrado"],
    motivo_cancelacion: null,
    foto_remito_url: "data:image/jpeg;base64,ZmFrZV9waG90bw==",
    monto_cobrado_real: "54100.00",
    estado_rendicion: "PENDIENTE",
    observacion_rendicion: null,
    rendido_en: null,
    rendido_por_id: null,
    creado_en: "2026-11-02T10:00:00Z",
    actualizado_en: "2026-11-02T12:00:00Z",
    ...parcial,
  };
}

describe("Ticket H10 - Rendición y POD en Frontend", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renderiza KPIs del panel de caja y lista servicios pendientes", () => {
    const s1 = crearServicioTest({
      id_servicio: 101,
      monto_cobrado_real: "54100.00",
      estado_rendicion: "PENDIENTE",
    });
    const s2 = crearServicioTest({
      id_servicio: 102,
      razon_social_cliente: "Distribuidora Sur",
      nombre_chofer: "El Ruso",
      monto_cobrado_real: "30000.00",
      estado_rendicion: "RENDIDO",
      estado: "cobrado",
    });

    render(<PanelCajaRendiciones serviciosIniciales={[s1, s2]} />);

    expect(screen.getByText("Dinero en Mano a Rendir")).toBeVisible();
    expect(screen.getByText("Rendido e Ingresado a Caja")).toBeVisible();
    expect(screen.getByText("Viajes con Remito (POD)")).toBeVisible();

    // Verificamos que aparece la fila del viaje #101
    expect(screen.getByText("#101")).toBeVisible();
    expect(screen.getByText("Ferretería Central")).toBeVisible();
    expect(screen.getAllByText("Marcelo Rodriguez").length).toBeGreaterThan(0);
  });

  it("permite abrir modal para ver remito firmado y aprobar rendición", async () => {
    const s1 = crearServicioTest({
      id_servicio: 101,
      foto_remito_url: "data:image/jpeg;base64,ZmFrZV9waG90bw==",
      estado_rendicion: "PENDIENTE",
    });

    aprobarRendicionAccion.mockResolvedValue({
      ok: true,
      dato: { ...s1, estado_rendicion: "RENDIDO", estado: "cobrado" },
    });

    render(<PanelCajaRendiciones serviciosIniciales={[s1]} />);

    // Clic en "Ver foto"
    const botonVerFoto = screen.getByRole("button", { name: /ver foto/i });
    fireEvent.click(botonVerFoto);

    // Modal de remito abierto
    expect(screen.getByText(/Prueba de Entrega \(POD\) — Viaje #101/i)).toBeVisible();

    // Clic en "Aprobar Rendición" desde la tabla o modal
    const botonesAprobar = screen.getAllByRole("button", {
      name: /aprobar/i,
    });
    fireEvent.click(botonesAprobar[0]);

    expect(aprobarRendicionAccion).toHaveBeenCalledWith(101);
  });

  it("ModalFinalizarViaje exige foto del remito antes de enviar", async () => {
    const s = crearServicioTest({ estado: "en curso" });
    const mockCerrar = vi.fn();

    render(<ModalFinalizarViaje servicio={s} abierto={true} alCerrar={mockCerrar} />);

    expect(screen.getByRole("heading", { name: /Finalizar Viaje #101/i })).toBeVisible();
    expect(
      screen.getByText(/1\. Foto del Remito Firmado \(Obligatorio\)/i),
    ).toBeVisible();
    expect(screen.getByText(/2\. Dinero Cobrado en Mano/i)).toBeVisible();

    // El botón debe estar deshabilitado mientras no haya foto cargada
    const botonSubmit = screen.getByRole("button", {
      name: /finalizar viaje y rendir/i,
    });
    expect(botonSubmit).toBeDisabled();
  });
});
