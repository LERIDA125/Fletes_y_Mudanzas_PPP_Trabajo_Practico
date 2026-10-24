import { z } from "zod";

export const esquemaVehiculo = z.object({
  patente: z
    .string()
    .trim()
    .min(6, "Ingresá la patente del vehículo.")
    .max(15, "La patente no puede superar los 15 caracteres."),
  id_tipo_vehiculo: z.string().min(1, "Elegí un tipo de vehículo."),
  id_chofer_habitual: z.string(),
});

export type ValoresVehiculo = z.input<typeof esquemaVehiculo>;
export type VehiculoValidado = {
  patente: string;
  id_tipo_vehiculo: number;
  id_chofer_habitual: number | null;
};

export const esquemaTarifasTipo = z.object({
  descripcion: z
    .string()
    .trim()
    .min(1, "Ingresá la descripción del tipo.")
    .max(120, "La descripción no puede superar los 120 caracteres."),
  capacidad_carga_kg: z
    .string()
    .min(1, "Ingresá la capacidad de carga.")
    .refine((valor) => Number.isFinite(Number(valor)) && Number(valor) > 0, {
      message: "La capacidad debe ser mayor que cero.",
    }),
  tarifa_hora_base: z
    .string()
    .min(1, "Ingresá la tarifa por hora.")
    .refine((valor) => Number.isFinite(Number(valor)) && Number(valor) >= 0, {
      message: "La tarifa por hora no puede ser negativa.",
    }),
  tarifa_km_excedente: z
    .string()
    .min(1, "Ingresá la tarifa por kilómetro.")
    .refine((valor) => Number.isFinite(Number(valor)) && Number(valor) >= 0, {
      message: "La tarifa por kilómetro no puede ser negativa.",
    }),
});

export type ValoresTarifasTipo = z.input<typeof esquemaTarifasTipo>;
export type TarifasTipoValidadas = {
  descripcion: string;
  capacidad_carga_kg: number;
  tarifa_hora_base: number;
  tarifa_km_excedente: number;
};
