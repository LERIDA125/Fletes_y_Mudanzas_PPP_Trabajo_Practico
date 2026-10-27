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

const {
  registrarServicio,
  solicitarCotizacion,
  consultarDisponibilidadServicio,
  obtenerCatalogosServicio,
  cambiarEstadoServicio,
  eliminarServicio,
  refresh,
} = vi.hoisted(() => ({
  registrarServicio: vi.fn(),
  solicitarCotizacion: vi.fn(),
  consultarDisponibilidadServicio: vi.fn(),
  obtenerCatalogosServicio: vi.fn(),
  cambiarEstadoServicio: vi.fn(),
  eliminarServicio: vi.fn(),
  refresh: vi.fn(),
}));

vi.mock("@/features/servicios/actions", () => ({
  registrarServicio,
  solicitarCotizacion,
  consultarDisponibilidadServicio,
  obtenerCatalogosServicio,
  cambiarEstadoServicio,
  eliminarServicio,
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
    hora_fin: null,
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
    motivo_cancelacion: null,
    creado_en: "2026-10-21T12:00:00Z",
    actualizado_en: "2026-10-21T12:00:00Z",
  };
}

const disponibilidad = {
  id_tipo_vehiculo: 3,
  fecha: "2026-10-25",
  hora_inicio: null,
  hora_fin: null,
  choferes: [],
  vehiculos: [],
};

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
    consultarDisponibilidadServicio.mockResolvedValue({
      ok: true,
      dato: disponibilidad,
    });
    obtenerCatalogosServicio.mockResolvedValue({
      ok: true,
      dato: { clientes, tiposVehiculo },
    });
  });

  it("abre el formulario automáticamente cuando llega abrirInicial", async () => {
    render(
      <FormularioServicio
        clientes={clientes}
        tiposVehiculo={tiposVehiculo}
        abrirInicial
      />,
    );

    await waitFor(() => expect(screen.getByRole("dialog")).toHaveAttribute("open"));
  });

  it("pide los catálogos al abrir cuando la página no los precarga", async () => {
    const usuario = userEvent.setup();
    render(<FormularioServicio />);

    expect(screen.queryByLabelText("Tipo de vehículo")).not.toBeInTheDocument();
    await usuario.click(screen.getByText("Nuevo servicio"));

    await waitFor(() => expect(obtenerCatalogosServicio).toHaveBeenCalledOnce());
    expect(await screen.findByLabelText("Tipo de vehículo")).toBeInTheDocument();
    expect(screen.getByLabelText("Cliente")).toBeInTheDocument();
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

  it("permite registrar el servicio con un cliente nuevo", async () => {
    const usuario = userEvent.setup();
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await usuario.click(screen.getByRole("button", { name: "Cliente nuevo" }));
    await usuario.type(screen.getByLabelText("Razón social"), "Mudanzas Sur");
    await usuario.type(screen.getByLabelText("Teléfono"), "3515550199");
    await usuario.type(screen.getByLabelText("Dirección habitual"), "Av. Colón 100");
    await usuario.selectOptions(screen.getByLabelText("Tipo de vehículo"), "3");
    fireEvent.change(screen.getByLabelText("Fecha"), {
      target: { value: "2026-10-25" },
    });
    fireEvent.change(screen.getByLabelText("Horas estimadas"), {
      target: { value: "2" },
    });
    fireEvent.change(screen.getByLabelText("Distancia de ida (km)"), {
      target: { value: "15" },
    });

    await usuario.click(screen.getByRole("button", { name: "Cotizar viaje" }));
    await screen.findByText(
      (texto, elemento) => elemento?.tagName === "STRONG" && texto.includes("9.000,00"),
    );
    await usuario.click(
      screen.getByRole("button", { name: "Confirmar y registrar servicio" }),
    );

    await waitFor(() => expect(registrarServicio).toHaveBeenCalledOnce());
    expect(registrarServicio).toHaveBeenCalledWith({
      nuevo_cliente: {
        razon_social: "Mudanzas Sur",
        telefono: "3515550199",
        direccion_habitual: "Av. Colón 100",
        tiene_cuenta_corriente: false,
      },
      id_tipo_vehiculo: 3,
      fecha: "2026-10-25",
      hora_inicio: null,
      horas_estimadas: 2,
      distancia_ida_km: 15,
    });
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
  beforeEach(() => {
    vi.clearAllMocks();
    cambiarEstadoServicio.mockResolvedValue({
      ok: true,
      dato: servicioCreado(),
    });
    eliminarServicio.mockResolvedValue({ ok: true, dato: undefined });
  });

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
    expect(fila).toHaveTextContent("Sin chofer");
    expect(fila).toHaveTextContent("Sin vehículo");
  });

  it("permite cambiar el estado y actualiza la tabla tras el éxito", async () => {
    const usuario = userEvent.setup();
    render(<ListadoServicios servicios={[servicioCreado()]} />);

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Mudanzas del Centro" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Cambiar estado" }));
    await usuario.selectOptions(screen.getByLabelText("Nuevo estado"), "en curso");
    await usuario.click(screen.getByRole("button", { name: "Guardar estado" }));

    await waitFor(() => {
      expect(cambiarEstadoServicio).toHaveBeenCalledWith(41, "en curso");
      expect(refresh).toHaveBeenCalledOnce();
    });
  });

  it("pide confirmación antes de eliminar el servicio", async () => {
    const usuario = userEvent.setup();
    const confirmacion = vi.spyOn(window, "confirm").mockReturnValue(false);
    render(<ListadoServicios servicios={[servicioCreado()]} />);

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Mudanzas del Centro" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Eliminar" }));

    expect(confirmacion).toHaveBeenCalledWith(
      "¿Eliminar el servicio de Mudanzas del Centro? Esta acción no se puede deshacer.",
    );
    expect(eliminarServicio).not.toHaveBeenCalled();
    expect(refresh).not.toHaveBeenCalled();

    confirmacion.mockReturnValue(true);
    await usuario.click(screen.getByRole("button", { name: "Eliminar" }));

    await waitFor(() => {
      expect(eliminarServicio).toHaveBeenCalledWith(41);
      expect(refresh).toHaveBeenCalledOnce();
    });
    confirmacion.mockRestore();
  });
});
