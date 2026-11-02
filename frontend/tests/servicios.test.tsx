import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { FormularioServicio } from "@/features/servicios/components/formulario-servicio";
import { ListadoServicios } from "@/features/servicios/components/listado-servicios";
import type {
  ClienteOpcion,
  Cotizacion,
  DireccionOpcion,
  ResultadoRuta,
  Servicio,
  TipoVehiculoOpcion,
} from "@/features/servicios/types";

const {
  registrarServicio,
  solicitarCotizacion,
  buscarDireccionesMapa,
  calcularRutaMapa,
  consultarDisponibilidadServicio,
  obtenerCatalogosServicio,
  cambiarEstadoServicio,
  cancelarServicio,
  eliminarServicio,
  refresh,
} = vi.hoisted(() => ({
  registrarServicio: vi.fn(),
  solicitarCotizacion: vi.fn(),
  buscarDireccionesMapa: vi.fn(),
  calcularRutaMapa: vi.fn(),
  consultarDisponibilidadServicio: vi.fn(),
  obtenerCatalogosServicio: vi.fn(),
  cambiarEstadoServicio: vi.fn(),
  cancelarServicio: vi.fn(),
  eliminarServicio: vi.fn(),
  refresh: vi.fn(),
}));

vi.mock("@/features/servicios/actions", () => ({
  registrarServicio,
  solicitarCotizacion,
  buscarDireccionesMapa,
  calcularRutaMapa,
  consultarDisponibilidadServicio,
  obtenerCatalogosServicio,
  cambiarEstadoServicio,
  cancelarServicio,
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

const origen: DireccionOpcion = {
  etiqueta: "Terminal de Ómnibus, Córdoba",
  longitud: "-64.1888",
  latitud: "-31.4201",
};

const destino: DireccionOpcion = {
  etiqueta: "Plaza San Martín, Córdoba",
  longitud: "-64.1833",
  latitud: "-31.4167",
};

const ruta: ResultadoRuta = {
  distancia_ida_km: "15.00",
  duracion_segundos: "3600",
};

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
  base_horas: "6000.00",
  base_km: "3000.00",
  subtotal_base: "9000.00",
  requiere_ayudante: false,
  recargo_ayudante: "0.00",
  acceso_escalera: false,
  recargo_escalera: "0.00",
  subtotal_con_fijos: "9000.00",
  zona_concurrida: false,
  porcentaje_zona_concurrida: "0.00",
  importe_recargo_zona_concurrida: "0.00",
  urgencia_mismo_dia: false,
  porcentaje_urgencia_mismo_dia: "0.00",
  importe_recargo_urgencia_mismo_dia: "0.00",
  total_recargos_porcentuales: "0.00",
  precio_sugerido: "9000.00",
  precio_final: "9000.00",
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
    distancia_ida_km: "15",
    origen_direccion: null,
    destino_direccion: null,
    distancia_total_km: "30",
    km_franquicia: "10",
    km_excedente: "20",
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
    porcentaje_zona_aplicado: "0.00",
    porcentaje_urgencia_aplicado: "0.00",
    precio_sugerido: "9000.00",
    precio_acordado: "9000.00",
    precio_total: "9000.00",
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
  vehiculos: [],
};

async function completarDatos() {
  await userEvent.selectOptions(screen.getByLabelText("Cliente"), "8");
  await userEvent.selectOptions(screen.getByLabelText("Tipo de vehículo"), "3");
  fireEvent.change(screen.getByLabelText("Fecha"), { target: { value: "2026-10-25" } });
  fireEvent.change(screen.getByLabelText("Horas estimadas"), { target: { value: "2" } });
  await seleccionarDireccion("Origen", "Origen Córdoba", origen);
  await seleccionarDireccion("Destino", "Destino Córdoba", destino);
  await waitFor(() =>
    expect(screen.getByLabelText("Distancia de ida (km)")).toHaveValue(15),
  );
  await screen.findByText(
    (texto, elemento) => elemento?.tagName === "STRONG" && texto.includes("9.000,00"),
  );
}

async function seleccionarDireccion(
  extremo: string,
  consulta: string,
  opcion: DireccionOpcion,
) {
  await userEvent.type(screen.getByLabelText(extremo), consulta);
  await userEvent.click(screen.getByRole("button", { name: `Buscar ${extremo}` }));
  await userEvent.click(await screen.findByRole("option", { name: opcion.etiqueta }));
}

describe("FormularioServicio", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    solicitarCotizacion.mockResolvedValue({ ok: true, dato: cotizacion });
    buscarDireccionesMapa.mockImplementation(async () => ({
      ok: true,
      dato: [origen, destino],
    }));
    calcularRutaMapa.mockResolvedValue({ ok: true, dato: ruta });
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

  it("busca direcciones solo al enviar la consulta explícitamente", async () => {
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);
    await userEvent.click(screen.getByText("Nuevo servicio"));
    await userEvent.type(screen.getByLabelText("Origen"), "Origen Córdoba");

    expect(buscarDireccionesMapa).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: "Buscar Origen" }));
    await waitFor(() => expect(buscarDireccionesMapa).toHaveBeenCalledOnce());
    expect(buscarDireccionesMapa).toHaveBeenCalledWith("Origen Córdoba");
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

  it("calcula la ruta, cotiza automáticamente y solo crea al confirmar", async () => {
    const usuario = userEvent.setup();
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await completarDatos();

    expect(
      await screen.findByText(
        (texto, elemento) => elemento?.tagName === "STRONG" && texto.includes("9.000,00"),
      ),
    ).toBeInTheDocument();
    expect(solicitarCotizacion).toHaveBeenCalledWith({
      id_tipo_vehiculo: 3,
      horas_estimadas: 2,
      distancia_ida_km: 15,
      requiere_ayudante: false,
      acceso_escalera: false,
      zona_concurrida: false,
      urgencia_mismo_dia: false,
    });
    expect(calcularRutaMapa).toHaveBeenCalledWith(
      { longitud: origen.longitud, latitud: origen.latitud },
      { longitud: destino.longitud, latitud: destino.latitud },
    );
    expect(screen.getByLabelText("Distancia de ida (km)")).toHaveAttribute("readonly");
    expect(screen.getByText("Tiempo estimado:")).toBeInTheDocument();
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
      requiere_ayudante: false,
      acceso_escalera: false,
      zona_concurrida: false,
      urgencia_mismo_dia: false,
      precio_acordado: 9000,
      origen_direccion: origen.etiqueta,
      destino_direccion: destino.etiqueta,
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
    await seleccionarDireccion("Origen", "Origen Córdoba", origen);
    await seleccionarDireccion("Destino", "Destino Córdoba", destino);
    await waitFor(() =>
      expect(screen.getByLabelText("Distancia de ida (km)")).toHaveValue(15),
    );
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
      requiere_ayudante: false,
      acceso_escalera: false,
      zona_concurrida: false,
      urgencia_mismo_dia: false,
      precio_acordado: 9000,
      origen_direccion: origen.etiqueta,
      destino_direccion: destino.etiqueta,
    });
  });

  it("recalcula automáticamente cuando cambian los datos de cotización", async () => {
    const usuario = userEvent.setup();
    solicitarCotizacion
      .mockResolvedValueOnce({ ok: true, dato: cotizacion })
      .mockResolvedValueOnce({
        ok: true,
        dato: {
          ...cotizacion,
          horas_estimadas: "3",
          base_horas: "9000.00",
          subtotal_base: "12000.00",
          subtotal_con_fijos: "12000.00",
          precio_sugerido: "12000.00",
          precio_final: "12000.00",
        },
      });
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await completarDatos();
    expect(
      await screen.findByText(
        (texto, elemento) => elemento?.tagName === "STRONG" && texto.includes("9.000,00"),
      ),
    ).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Horas estimadas"), {
      target: { value: "3" },
    });

    expect(
      await screen.findByText(
        (texto, elemento) =>
          elemento?.tagName === "STRONG" && texto.includes("12.000,00"),
      ),
    ).toBeInTheDocument();
    expect(solicitarCotizacion).toHaveBeenCalledTimes(2);
  });

  it("recalcula por modificadores, permite acordar otro precio y lo registra", async () => {
    const usuario = userEvent.setup();
    solicitarCotizacion
      .mockResolvedValueOnce({ ok: true, dato: cotizacion })
      .mockResolvedValueOnce({
        ok: true,
        dato: {
          ...cotizacion,
          zona_concurrida: true,
          porcentaje_zona_concurrida: "15.00",
          importe_recargo_zona_concurrida: "1350.00",
          total_recargos_porcentuales: "1350.00",
          precio_sugerido: "10350.00",
          precio_final: "10350.00",
        },
      });
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await completarDatos();
    await usuario.click(screen.getByLabelText("Zona concurrida"));

    expect(
      await screen.findByText(
        (texto, elemento) =>
          elemento?.tagName === "STRONG" && texto.includes("10.350,00"),
      ),
    ).toBeInTheDocument();
    expect(solicitarCotizacion).toHaveBeenLastCalledWith({
      id_tipo_vehiculo: 3,
      horas_estimadas: 2,
      distancia_ida_km: 15,
      requiere_ayudante: false,
      acceso_escalera: false,
      zona_concurrida: true,
      urgencia_mismo_dia: false,
    });

    const precioAcordado = screen.getByLabelText("Precio final acordado");
    expect(precioAcordado).toHaveValue(10350);
    await usuario.clear(precioAcordado);
    await usuario.type(precioAcordado, "8000");
    await usuario.click(
      screen.getByRole("button", { name: "Confirmar y registrar servicio" }),
    );

    await waitFor(() => expect(registrarServicio).toHaveBeenCalledOnce());
    expect(registrarServicio).toHaveBeenCalledWith(
      expect.objectContaining({
        zona_concurrida: true,
        precio_acordado: 8000,
      }),
    );
  }, 15000);

  it("permite reintentar una ruta fallida sin conservar kilómetros anteriores", async () => {
    calcularRutaMapa
      .mockResolvedValueOnce({ ok: false, mensaje: "No encontramos una ruta." })
      .mockResolvedValueOnce({ ok: true, dato: ruta });
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await userEvent.click(screen.getByText("Nuevo servicio"));
    await userEvent.selectOptions(screen.getByLabelText("Cliente"), "8");
    await userEvent.selectOptions(screen.getByLabelText("Tipo de vehículo"), "3");
    fireEvent.change(screen.getByLabelText("Fecha"), {
      target: { value: "2026-10-25" },
    });
    fireEvent.change(screen.getByLabelText("Horas estimadas"), {
      target: { value: "2" },
    });
    await seleccionarDireccion("Origen", "Origen Córdoba", origen);
    await seleccionarDireccion("Destino", "Destino Córdoba", destino);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "No encontramos una ruta.",
    );
    expect(screen.getByLabelText("Distancia de ida (km)")).toHaveValue(null);
    await userEvent.click(screen.getByRole("button", { name: "Reintentar cálculo" }));
    await waitFor(() =>
      expect(screen.getByLabelText("Distancia de ida (km)")).toHaveValue(15),
    );
    expect(calcularRutaMapa).toHaveBeenCalledTimes(2);
  });

  it("ignora la respuesta de una ruta que quedó obsoleta al cambiar el origen", async () => {
    let resolverRutaAntigua:
      ((respuesta: { ok: true; dato: ResultadoRuta }) => void) | undefined;
    calcularRutaMapa
      .mockImplementationOnce(
        () =>
          new Promise<{ ok: true; dato: ResultadoRuta }>((resolve) => {
            resolverRutaAntigua = resolve;
          }),
      )
      .mockResolvedValueOnce({ ok: true, dato: ruta });
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await userEvent.click(screen.getByText("Nuevo servicio"));
    await userEvent.selectOptions(screen.getByLabelText("Cliente"), "8");
    await userEvent.selectOptions(screen.getByLabelText("Tipo de vehículo"), "3");
    fireEvent.change(screen.getByLabelText("Fecha"), {
      target: { value: "2026-10-25" },
    });
    fireEvent.change(screen.getByLabelText("Horas estimadas"), {
      target: { value: "2" },
    });
    await seleccionarDireccion("Origen", "Origen Córdoba", origen);
    await seleccionarDireccion("Destino", "Destino Córdoba", destino);
    await waitFor(() => expect(calcularRutaMapa).toHaveBeenCalledOnce());

    fireEvent.change(screen.getByLabelText("Origen"), {
      target: { value: "Nuevo origen Córdoba" },
    });
    await seleccionarDireccion("Origen", "Origen alternativo", origen);
    await waitFor(() => expect(calcularRutaMapa).toHaveBeenCalledTimes(2));
    await waitFor(() =>
      expect(screen.getByLabelText("Distancia de ida (km)")).toHaveValue(15),
    );
    await screen.findByText(
      (texto, elemento) => elemento?.tagName === "STRONG" && texto.includes("9.000,00"),
    );

    resolverRutaAntigua?.({
      ok: true,
      dato: { ...ruta, distancia_ida_km: "99.00" },
    });
    await waitFor(() =>
      expect(screen.getByLabelText("Distancia de ida (km)")).toHaveValue(15),
    );
    expect(solicitarCotizacion).toHaveBeenCalledWith({
      id_tipo_vehiculo: 3,
      horas_estimadas: 2,
      distancia_ida_km: 15,
      requiere_ayudante: false,
      acceso_escalera: false,
      zona_concurrida: false,
      urgencia_mismo_dia: false,
    });
  });

  it("preserva los datos y explica los errores devueltos por el servidor", async () => {
    const usuario = userEvent.setup();
    solicitarCotizacion.mockResolvedValue({ ok: false, mensaje: "No se pudo cotizar." });
    render(<FormularioServicio clientes={clientes} tiposVehiculo={tiposVehiculo} />);

    await usuario.click(screen.getByText("Nuevo servicio"));
    await usuario.selectOptions(screen.getByLabelText("Cliente"), "8");
    await usuario.selectOptions(screen.getByLabelText("Tipo de vehículo"), "3");
    fireEvent.change(screen.getByLabelText("Fecha"), {
      target: { value: "2026-10-25" },
    });
    fireEvent.change(screen.getByLabelText("Horas estimadas"), {
      target: { value: "2" },
    });
    await seleccionarDireccion("Origen", "Origen Córdoba", origen);
    await seleccionarDireccion("Destino", "Destino Córdoba", destino);

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
