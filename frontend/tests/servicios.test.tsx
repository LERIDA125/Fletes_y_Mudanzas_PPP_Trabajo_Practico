import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { FormularioServicio } from "@/features/servicios/components/formulario-servicio";
import { ListadoServicios } from "@/features/servicios/components/listado-servicios";
import type {
  ClienteOpcion,
  Cotizacion,
  Servicio,
  TipoVehiculoOpcion,
} from "@/features/servicios/types";

const { registrarServicio, solicitarCotizacion, refresh } = vi.hoisted(() => ({
  registrarServicio: vi.fn(),
  solicitarCotizacion: vi.fn(),
  refresh: vi.fn(),
}));

vi.mock("@/features/servicios/actions", () => ({
  registrarServicio,
  solicitarCotizacion,
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

const clientes: ClienteOpcion[] = [
  {
    id: 8,
    razon_social: "Mudanzas del Centro",
    telefono: "3515550100",
    direccion_habitual: "Córdoba",
    tiene_cuenta_corriente: false,
    activo: true,
    creado_en: "2026-10-01T12:00:00Z",
    actualizado_en: "2026-10-01T12:00:00Z",
  },
];

const tiposVehiculo: TipoVehiculoOpcion[] = [
  {
    id: 3,
    descripcion: "Furgón grande",
    capacidad_carga_kg: "1500",
    tarifa_hora_base: "3000",
    tarifa_km_excedente: "150",
    activo: true,
  },
];

const cotizacion: Cotizacion = {
  id_tipo_vehiculo: 3,
  descripcion_tipo_vehiculo: "Furgón grande",
  horas_estimadas: "2",
  distancia_ida_km: "15",
  distancia_total_km: "30",
  km_franquicia: "10",
  km_excedente: "20",
  tarifa_hora_base: "3000",
  tarifa_km_excedente: "150",
  precio_final: "9000.00",
  moneda: "ARS",
};

function servicioCreado(): Servicio {
  return {
    id_servicio: 41,
    id_cliente: 8,
    razon_social_cliente: "Mudanzas del Centro",
    id_tipo_vehiculo: 3,
    descripcion_tipo_vehiculo: "Furgón grande",
    id_chofer: null,
    nombre_chofer: null,
    id_vehiculo: null,
    patente_vehiculo: null,
    fecha: "2026-10-25",
    hora_inicio: null,
    horas_estimadas: "2",
    distancia_ida_km: "15",
    distancia_total_km: "30",
    km_franquicia: "10",
    km_excedente: "20",
    tarifa_hora_aplicada: "3000",
    tarifa_km_aplicada: "150",
    precio_total: "9000.00",
    moneda: "ARS",
    estado: "pendiente",
    creado_en: "2026-10-21T12:00:00Z",
    actualizado_en: "2026-10-21T12:00:00Z",
  };
}

async function completarDatos() {
  await userEvent.selectOptions(screen.getByLabelText("Cliente"), "8");
  await userEvent.selectOptions(screen.getByLabelText("Tipo de vehículo"), "3");
  fireEvent.change(screen.getByLabelText("Fecha"), { target: { value: "2026-10-25" } });
  fireEvent.change(screen.getByLabelText("Horas estimadas"), { target: { value: "2" } });
  fireEvent.change(screen.getByLabelText("Distancia de ida (km)"), {
    target: { value: "15" },
  });
}

describe("FormularioServicio", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    solicitarCotizacion.mockResolvedValue({ ok: true, dato: cotizacion });
    registrarServicio.mockResolvedValue({ ok: true, dato: servicioCreado() });
  });

  it("cotiza con el backend y solo crea después de confirmar la estimación", async () => {
    const usuario = userEvent.setup();
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await completarDatos();
    await usuario.click(screen.getByRole("button", { name: "Cotizar viaje" }));

    expect(
      await screen.findByText(
        (texto, elemento) => elemento?.tagName === "STRONG" && texto.includes("9.000,00"),
      ),
    ).toBeInTheDocument();
    expect(solicitarCotizacion).toHaveBeenCalledWith({
      id_tipo_vehiculo: 3,
      horas_estimadas: 2,
      distancia_ida_km: 15,
    });
    expect(registrarServicio).not.toHaveBeenCalled();

    await usuario.click(
      screen.getByRole("button", { name: "Confirmar y registrar servicio" }),
    );

    await waitFor(() => expect(registrarServicio).toHaveBeenCalledOnce());
    expect(registrarServicio).toHaveBeenCalledWith({
      id_cliente: 8,
      id_tipo_vehiculo: 3,
      fecha: "2026-10-25",
      hora_inicio: null,
      horas_estimadas: 2,
      distancia_ida_km: 15,
    });
    expect(await screen.findByRole("status")).toHaveTextContent(
      "Servicio #41 registrado. Precio final: $ 9.000,00.",
    );
    expect(refresh).toHaveBeenCalledOnce();
  });

  it("invalida la cotización y bloquea el alta si cambian los datos", async () => {
    const usuario = userEvent.setup();
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await completarDatos();
    await usuario.click(screen.getByRole("button", { name: "Cotizar viaje" }));
    expect(
      await screen.findByText(
        (texto, elemento) => elemento?.tagName === "STRONG" && texto.includes("9.000,00"),
      ),
    ).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Horas estimadas"), {
      target: { value: "3" },
    });

    expect(screen.getByText("La cotización quedó desactualizada")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Confirmar y registrar servicio" }),
    ).not.toBeInTheDocument();
    expect(registrarServicio).not.toHaveBeenCalled();
  });

  it("preserva los datos y explica los errores devueltos por el servidor", async () => {
    const usuario = userEvent.setup();
    solicitarCotizacion.mockResolvedValue({ ok: false, mensaje: "No se pudo cotizar." });
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await completarDatos();
    await usuario.click(screen.getByRole("button", { name: "Cotizar viaje" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cotizar.");
    expect(screen.getByLabelText("Horas estimadas")).toHaveValue(2);
    expect(screen.getByLabelText("Cliente")).toHaveValue("8");
  });
});

describe("ListadoServicios", () => {
  it("muestra asociaciones legibles, fecha, estado e importe del backend", () => {
    render(<ListadoServicios servicios={[servicioCreado()]} />);

    expect(
      screen.getByRole("table", { name: "Servicios registrados" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("rowheader")).toHaveTextContent("Mudanzas del Centro");
    expect(screen.getByText("Furgón grande")).toBeInTheDocument();
    expect(screen.getByText("25/10/2026")).toBeInTheDocument();
    const fila = screen.getByRole("rowheader").closest("tr");
    expect(fila).not.toBeNull();
    expect(fila).toHaveTextContent("9.000,00");
    expect(fila).toHaveTextContent("Sin vehículo · Sin chofer");
  });
});
