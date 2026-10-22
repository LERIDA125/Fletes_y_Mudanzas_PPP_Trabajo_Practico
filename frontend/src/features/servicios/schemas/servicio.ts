import { z } from "zod";

export const esquemaFormularioServicio = z.object({
  id_cliente: z.string().min(1, "Elegí un cliente."),
  id_tipo_vehiculo: z.string().min(1, "Elegí un tipo de vehículo."),
  fecha: z.string().min(1, "Ingresá la fecha del servicio."),
  hora_inicio: z.string(),
  horas_estimadas: z
    .string()
    .min(1, "Ingresá las horas estimadas.")
    .refine((valor) => Number.isFinite(Number(valor)) && Number(valor) >= 1, {
      message: "Las horas deben ser 1 o más.",
    }),
  distancia_ida_km: z
    .string()
    .min(1, "Ingresá los kilómetros de ida.")
    .refine((valor) => Number.isFinite(Number(valor)) && Number(valor) >= 0, {
      message: "La distancia no puede ser negativa.",
    }),
});

export type ValoresFormularioServicio = z.input<typeof esquemaFormularioServicio>;
