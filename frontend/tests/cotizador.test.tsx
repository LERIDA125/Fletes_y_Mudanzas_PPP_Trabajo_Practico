import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Cotizador } from "@/features/cotizaciones/components/cotizador";
import type {
  Cotizacion,
  DireccionOpcion,
  ResultadoRuta,
  TipoVehiculoOpcion,
} from "@/features/servicios/types";

const {
  buscarDireccionesMapa,
  calcularRutaMapa,
  solicitarCotizacion,
  registrarServicio,
} = vi.hoisted(() => ({
  buscarDireccionesMapa: vi.fn(),
  calcularRutaMapa: vi.fn(),
  solicitarCotizacion: vi.fn(),
  registrarServicio: vi.fn(),
}));

vi.mock("@/features/servicios/actions", () => ({
  buscarDireccionesMapa,
  calcularRutaMapa,
  solicitarCotizacion,
  registrarServicio,
}));

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
  distancia_ida_km: "15.00",
  distancia_total_km: "30.00",
  km_franquicia: "10.00",
  km_excedente: "20.00",
  tarifa_hora_base: "3000.00",
  tarifa_km_excedente: "150.00",
  base_horas: "6000.00",
  base_km: "3000.00",
  subtotal_base: "9000.00",
  requiere_ayudante: true,
  recargo_ayudante: "1000.00",
  acceso_escalera: true,
  recargo_escalera: "500.00",
  subtotal_con_fijos: "10500.00",
  zona_concurrida: true,
  porcentaje_zona_concurrida: "10.00",
  importe_recargo_zona_concurrida: "1050.00",
  urgencia_mismo_dia: true,
  porcentaje_urgencia_mismo_dia: "15.00",
  importe_recargo_urgencia_mismo_dia: "1575.00",
  total_recargos_porcentuales: "2625.00",
  precio_sugerido: "13125.00",
  precio_final: "13125.00",
  moneda: "ARS",
};

async function seleccionarDireccion(
  usuario: ReturnType<typeof userEvent.setup>,
  etiqueta: string,
  direccion: DireccionOpcion,
) {
  await usuario.type(
    screen.getByRole("searchbox", { name: etiqueta }),
    direccion.etiqueta,
  );
  await usuario.click(screen.getByRole("button", { name: `Buscar ${etiqueta}` }));
  await usuario.click(await screen.findByRole("option", { name: direccion.etiqueta }));
}

describe("Cotizador", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    buscarDireccionesMapa.mockResolvedValue({ ok: true, dato: [origen, destino] });
    calcularRutaMapa.mockResolvedValue({ ok: true, dato: ruta });
    solicitarCotizacion.mockResolvedValue({ ok: true, dato: cotizacion });
  });

  it("cotiza con la ruta y los modificadores seleccionados, sin crear un servicio", async () => {
    const user = userEvent.setup();
    render(<Cotizador tiposVehiculo={tiposVehiculo} />);

    await seleccionarDireccion(user, "Origen", origen);
    await seleccionarDireccion(user, "Destino", destino);
    await waitFor(() => expect(calcularRutaMapa).toHaveBeenCalledOnce());
    await waitFor(() =>
      expect(screen.getByLabelText("Distancia de ida (km)")).toHaveValue(15),
    );
    expect(screen.getByText("Tiempo estimado:")).toBeInTheDocument();

    for (const condicion of [
      "Requiere ayudante",
      "Acceso por escalera",
      "Zona concurrida",
      "Urgencia para el mismo día",
    ]) {
      await user.click(screen.getByRole("checkbox", { name: condicion }));
    }

    await user.click(screen.getByRole("button", { name: "Cotizar con el servidor" }));

    await waitFor(() =>
      expect(solicitarCotizacion).toHaveBeenCalledWith({
        id_tipo_vehiculo: 3,
        horas_estimadas: 2,
        distancia_ida_km: 15,
        requiere_ayudante: true,
        acceso_escalera: true,
        zona_concurrida: true,
        urgencia_mismo_dia: true,
      }),
    );
    expect(await screen.findByText("Base por horas")).toBeInTheDocument();
    expect(screen.getByText("Total de recargos porcentuales")).toBeInTheDocument();
    expect(screen.getAllByText("Precio sugerido").length).toBeGreaterThan(0);
    expect(registrarServicio).not.toHaveBeenCalled();
  });

  it("invalida la cotización cuando cambian las condiciones del viaje", async () => {
    const user = userEvent.setup();
    render(<Cotizador tiposVehiculo={tiposVehiculo} />);

    await seleccionarDireccion(user, "Origen", origen);
    await seleccionarDireccion(user, "Destino", destino);
    await waitFor(() => expect(calcularRutaMapa).toHaveBeenCalledOnce());
    await waitFor(() =>
      expect(screen.getByLabelText("Distancia de ida (km)")).toHaveValue(15),
    );
    await user.click(
      await screen.findByRole("button", { name: "Cotizar con el servidor" }),
    );
    await screen.findByText("Base por horas");

    await user.click(screen.getByRole("checkbox", { name: "Requiere ayudante" }));

    expect(screen.queryByText("Base por horas")).not.toBeInTheDocument();
    expect(solicitarCotizacion).toHaveBeenCalledOnce();
    expect(registrarServicio).not.toHaveBeenCalled();
  });

  it("muestra el error de ruta y no permite cotizar si el cálculo falla", async () => {
    const user = userEvent.setup();
    calcularRutaMapa.mockResolvedValueOnce({
      ok: false,
      mensaje: "No encontramos una ruta para esas direcciones.",
    });
    render(<Cotizador tiposVehiculo={tiposVehiculo} />);

    await seleccionarDireccion(user, "Origen", origen);
    await seleccionarDireccion(user, "Destino", destino);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "No encontramos una ruta para esas direcciones.",
    );
    expect(
      screen.getByRole("button", { name: "Cotizar con el servidor" }),
    ).toBeDisabled();
    expect(solicitarCotizacion).not.toHaveBeenCalled();
    expect(registrarServicio).not.toHaveBeenCalled();
  });
});
