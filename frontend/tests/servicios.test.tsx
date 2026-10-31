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
  calcularCotizacion,
  consultarDisponibilidadServicio,
  obtenerCatalogosServicio,
  cambiarEstadoServicio,
  cancelarServicio,
  eliminarServicio,
  refresh,
} = vi.hoisted(() => ({
  registrarServicio: vi.fn(),
  calcularCotizacion: vi.fn(),
  consultarDisponibilidadServicio: vi.fn(),
  obtenerCatalogosServicio: vi.fn(),
  cambiarEstadoServicio: vi.fn(),
  cancelarServicio: vi.fn(),
  eliminarServicio: vi.fn(),
  refresh: vi.fn(),
}));

vi.mock("@/features/servicios/actions", () => ({
  registrarServicio,
  consultarDisponibilidadServicio,
  obtenerCatalogosServicio,
  cambiarEstadoServicio,
  cancelarServicio,
  eliminarServicio,
}));

vi.mock("@/features/cotizaciones/actions", () => ({
  calcularCotizacion,
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
    creado_en: "2026-10-01T12:00:00Z",
    actualizado_en: "2026-10-01T12:00:00Z",
  },
  {
    id: 4,
    descripcion: "Camioneta",
    capacidad_carga_kg: "1000",
    tarifa_hora_base: "2500",
    tarifa_km_excedente: "100",
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
  tarifa_hora_base: "3000",
  tarifa_km_excedente: "150",
  base_horas: "6000.00",
  base_km: "2250.00",
  subtotal_base: "8250.00",
  requiere_ayudante: false,
  recargo_ayudante: "30000.00",
  acceso_escalera: false,
  recargo_escalera: "15000.00",
  subtotal_con_fijos: "8250.00",
  zona_concurrida: false,
  porcentaje_zona_concurrida: "15.00",
  importe_recargo_zona_concurrida: "0.00",
  urgencia_mismo_dia: false,
  porcentaje_urgencia_mismo_dia: "20.00",
  importe_recargo_urgencia_mismo_dia: "0.00",
  total_recargos_porcentuales: "0.00",
  precio_sugerido: "8250.00",
  moneda: "ARS",
};

function servicioCreado(parcial: Partial<Servicio> = {}): Servicio {
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
    km_estimados: "15",
    distancia_total_km: "0",
    km_franquicia: "0",
    km_excedente: "0",
    tarifa_hora_aplicada: "3000",
    tarifa_km_aplicada: "150",
    requiere_ayudante: false,
    acceso_escalera: false,
    zona_concurrida: false,
    urgencia_mismo_dia: false,
    recargo_ayudante_aplicado: "0.00",
    recargo_escalera_aplicado: "0.00",
    importe_recargo_zona_aplicado: "0.00",
    importe_recargo_urgencia_aplicado: "0.00",
    porcentaje_zona_aplicado: "15.00",
    porcentaje_urgencia_aplicado: "20.00",
    precio_sugerido: "8250.00",
    precio_acordado: "9000.00",
    moneda: "ARS",
    estado: "pendiente",
    transiciones_validas: ["confirmado", "cancelado"],
    motivo_cancelacion: null,
    creado_en: "2026-10-21T12:00:00Z",
    actualizado_en: "2026-10-21T12:00:00Z",
    ...parcial,
  };
}

const disponibilidad = {
  id_tipo_vehiculo: 3,
  fecha: "2026-10-25",
  hora_inicio: null,
  hora_fin: null,
  choferes: [],
  vehiculos: [
    {
      id: 12,
      patente: "ABC123",
      id_tipo_vehiculo: 3,
      id_chofer_habitual: null,
      descripcion_tipo_vehiculo: "Furgón grande",
      capacidad_carga_kg: "1500",
      nombre_chofer_habitual: null,
      activo: true,
      creado_en: "2026-10-01T12:00:00Z",
      actualizado_en: "2026-10-01T12:00:00Z",
    },
    {
      id: 13,
      patente: "XYZ987",
      id_tipo_vehiculo: 4,
      id_chofer_habitual: null,
      descripcion_tipo_vehiculo: "Camioneta",
      capacidad_carga_kg: "1000",
      nombre_chofer_habitual: null,
      activo: true,
      creado_en: "2026-10-01T12:00:00Z",
      actualizado_en: "2026-10-01T12:00:00Z",
    },
  ],
};

async function completarDatos() {
  await userEvent.selectOptions(screen.getByLabelText("Cliente"), "8");
  await userEvent.selectOptions(screen.getByLabelText("Tipo de vehículo"), "3");
  fireEvent.change(screen.getByLabelText("Fecha"), { target: { value: "2026-10-25" } });
  fireEvent.change(screen.getByLabelText("Horas estimadas"), { target: { value: "2" } });
  fireEvent.change(screen.getByLabelText("Kilómetros estimados"), {
    target: { value: "15" },
  });
}

describe("FormularioServicio", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    calcularCotizacion.mockResolvedValue({ ok: true, dato: cotizacion });
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

  it("cotiza al cambiar los datos y registra el precio sugerido sin requerir un botón de cotización", async () => {
    const usuario = userEvent.setup();
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await completarDatos();

    expect(
      await screen.findByText(
        (texto, elemento) => elemento?.tagName === "STRONG" && texto.includes("8.250,00"),
      ),
    ).toBeInTheDocument();
    expect(calcularCotizacion).toHaveBeenCalledWith({
      id_tipo_vehiculo: 3,
      horas_estimadas: 2,
      km_estimados: 15,
      requiere_ayudante: false,
      acceso_escalera: false,
      zona_concurrida: false,
      urgencia_mismo_dia: false,
    });

    await usuario.click(screen.getByRole("button", { name: "Registrar servicio" }));

    await waitFor(() => expect(registrarServicio).toHaveBeenCalledOnce());
    expect(registrarServicio).toHaveBeenCalledWith({
      id_cliente: 8,
      id_tipo_vehiculo: 3,
      fecha: "2026-10-25",
      hora_inicio: null,
      horas_estimadas: 2,
      km_estimados: 15,
      requiere_ayudante: false,
      acceso_escalera: false,
      zona_concurrida: false,
      urgencia_mismo_dia: false,
      precio_acordado: 8250,
    });
    expect(await screen.findByRole("status")).toHaveTextContent(
      "Servicio #41 registrado. Precio acordado: $ 9.000,00.",
    );
    expect(refresh).toHaveBeenCalledOnce();
  });

  it("filtra las unidades por categoría y limpia la asignación al cambiarla", async () => {
    const usuario = userEvent.setup();
    consultarDisponibilidadServicio.mockImplementation(
      async ({ id_tipo_vehiculo }: { id_tipo_vehiculo: number }) => ({
        ok: true,
        dato: { ...disponibilidad, id_tipo_vehiculo },
      }),
    );
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await completarDatos();
    const unidad = screen.getByLabelText("Unidad asignada");

    await screen.findByRole("option", { name: "ABC123" });
    expect(screen.queryByRole("option", { name: "XYZ987" })).not.toBeInTheDocument();

    await usuario.selectOptions(unidad, "12");
    expect(unidad).toHaveValue("12");

    await usuario.selectOptions(screen.getByLabelText("Tipo de vehículo"), "4");

    expect(unidad).toHaveValue("");
    expect(screen.queryByRole("option", { name: "ABC123" })).not.toBeInTheDocument();
    expect(await screen.findByRole("option", { name: "XYZ987" })).toBeInTheDocument();
    expect(screen.queryByRole("option", { name: "ABC123" })).not.toBeInTheDocument();
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
    fireEvent.change(screen.getByLabelText("Kilómetros estimados"), {
      target: { value: "15" },
    });

    await screen.findByText(
      (texto, elemento) => elemento?.tagName === "STRONG" && texto.includes("8.250,00"),
    );
    await usuario.click(screen.getByRole("button", { name: "Registrar servicio" }));

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
      km_estimados: 15,
      requiere_ayudante: false,
      acceso_escalera: false,
      zona_concurrida: false,
      urgencia_mismo_dia: false,
      precio_acordado: 8250,
    });
  });

  it("mantiene el importe editado aunque cambie la cotización", async () => {
    const usuario = userEvent.setup();
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await completarDatos();
    expect(
      await screen.findByText(
        (texto, elemento) => elemento?.tagName === "STRONG" && texto.includes("8.250,00"),
      ),
    ).toBeInTheDocument();
    const precio = screen.getByLabelText("Precio final acordado");
    expect(precio).toHaveValue(8250);
    await usuario.clear(precio);
    await usuario.type(precio, "7000");

    fireEvent.change(screen.getByLabelText("Horas estimadas"), {
      target: { value: "3" },
    });

    await waitFor(
      () =>
        expect(calcularCotizacion).toHaveBeenCalledWith(
          expect.objectContaining({ horas_estimadas: 3 }),
        ),
      { timeout: 2000 },
    );
    expect(precio).toHaveValue(7000);
    await usuario.click(screen.getByRole("button", { name: "Registrar servicio" }));
    await waitFor(() =>
      expect(registrarServicio).toHaveBeenCalledWith(
        expect.objectContaining({ precio_acordado: 7000 }),
      ),
    );
  });

  it("permite registrar con un precio manual aunque falle la cotización", async () => {
    const usuario = userEvent.setup();
    calcularCotizacion.mockResolvedValue({ ok: false, mensaje: "No se pudo cotizar." });
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await completarDatos();
    await usuario.type(screen.getByLabelText("Precio final acordado"), "5000");

    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cotizar.");
    expect(screen.getByLabelText("Horas estimadas")).toHaveValue(2);
    expect(screen.getByLabelText("Cliente")).toHaveValue("8");
    await usuario.click(screen.getByRole("button", { name: "Registrar servicio" }));
    await waitFor(() =>
      expect(registrarServicio).toHaveBeenCalledWith(
        expect.objectContaining({ precio_acordado: 5000 }),
      ),
    );
  });
});

describe("ListadoServicios", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    cambiarEstadoServicio.mockResolvedValue({
      ok: true,
      dato: servicioCreado(),
    });
    cancelarServicio.mockResolvedValue({
      ok: true,
      dato: servicioCreado({ estado: "cancelado" }),
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

  it("solo ofrece las transiciones que declara el backend y preselecciona la primera", async () => {
    const usuario = userEvent.setup();
    render(<ListadoServicios servicios={[servicioCreado()]} />);

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Mudanzas del Centro" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Cambiar estado" }));

    const selector = screen.getByLabelText("Nuevo estado");
    expect(selector).toHaveValue("confirmado");
    expect(screen.getAllByRole("option").map((opcion) => opcion.textContent)).toEqual([
      "Confirmado",
      "Cancelado",
    ]);
  });

  it("cambia el estado con una transición válida y actualiza la tabla", async () => {
    const usuario = userEvent.setup();
    render(<ListadoServicios servicios={[servicioCreado()]} />);

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Mudanzas del Centro" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Cambiar estado" }));
    await usuario.selectOptions(screen.getByLabelText("Nuevo estado"), "confirmado");
    await usuario.click(screen.getByRole("button", { name: "Actualizar estado" }));

    await waitFor(() => {
      expect(cambiarEstadoServicio).toHaveBeenCalledWith(41, "confirmado");
      expect(refresh).toHaveBeenCalledOnce();
    });
  });

  it("muestra el detalle de negocio que devuelve la API en vez de un texto genérico", async () => {
    const usuario = userEvent.setup();
    cambiarEstadoServicio.mockResolvedValue({
      ok: false,
      mensaje: "No se puede pasar el servicio de pendiente a finalizado.",
    });
    render(<ListadoServicios servicios={[servicioCreado()]} />);

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Mudanzas del Centro" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Cambiar estado" }));
    await usuario.click(screen.getByRole("button", { name: "Actualizar estado" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "No se puede pasar el servicio de pendiente a finalizado.",
    );
    expect(refresh).not.toHaveBeenCalled();
  });

  it("cancela por el endpoint de cancelación y exige el motivo", async () => {
    const usuario = userEvent.setup();
    render(<ListadoServicios servicios={[servicioCreado()]} />);

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Mudanzas del Centro" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Cambiar estado" }));
    await usuario.selectOptions(screen.getByLabelText("Nuevo estado"), "cancelado");

    await usuario.click(screen.getByRole("button", { name: "Cancelar servicio" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Indicá el motivo de la cancelación.",
    );
    expect(cancelarServicio).not.toHaveBeenCalled();

    await usuario.type(
      screen.getByLabelText("Motivo de la cancelación"),
      "El cliente reprogramó",
    );
    await usuario.click(screen.getByRole("button", { name: "Cancelar servicio" }));

    await waitFor(() => {
      expect(cancelarServicio).toHaveBeenCalledWith(41, "El cliente reprogramó");
      expect(refresh).toHaveBeenCalledOnce();
    });
  });

  it("no ofrece cambios de estado cuando el servicio está en un estado final", async () => {
    const usuario = userEvent.setup();
    render(
      <ListadoServicios
        servicios={[servicioCreado({ estado: "cobrado", transiciones_validas: [] })]}
      />,
    );

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Mudanzas del Centro" }),
    );

    expect(
      screen.queryByRole("button", { name: "Cambiar estado" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByText("El servicio está en un estado final: no admite más cambios."),
    ).toBeInTheDocument();
  });

  it("cierra el menú con Escape y al hacer clic afuera", async () => {
    const usuario = userEvent.setup();
    render(<ListadoServicios servicios={[servicioCreado()]} />);
    const opciones = screen.getByRole("button", {
      name: "Opciones de Mudanzas del Centro",
    });

    await usuario.click(opciones);
    expect(screen.getByRole("button", { name: "Cambiar estado" })).toBeInTheDocument();

    await usuario.keyboard("{Escape}");
    expect(
      screen.queryByRole("button", { name: "Cambiar estado" }),
    ).not.toBeInTheDocument();
    expect(opciones).toHaveFocus();

    await usuario.click(opciones);
    expect(screen.getByRole("button", { name: "Cambiar estado" })).toBeInTheDocument();

    await usuario.click(document.body);
    expect(
      screen.queryByRole("button", { name: "Cambiar estado" }),
    ).not.toBeInTheDocument();
  });

  it("pide confirmación antes de eliminar el servicio", async () => {
    const usuario = userEvent.setup();
    render(<ListadoServicios servicios={[servicioCreado()]} />);

    await usuario.click(
      screen.getByRole("button", { name: "Opciones de Mudanzas del Centro" }),
    );
    await usuario.click(screen.getByRole("button", { name: "Eliminar" }));

    expect(await screen.findByRole("dialog")).toHaveTextContent("Eliminar servicio");
    expect(eliminarServicio).not.toHaveBeenCalled();
    expect(refresh).not.toHaveBeenCalled();

    await usuario.click(screen.getByRole("button", { name: "Sí, eliminar" }));

    await waitFor(() => {
      expect(eliminarServicio).toHaveBeenCalledWith(41);
      expect(refresh).toHaveBeenCalledOnce();
    });
  });
});
