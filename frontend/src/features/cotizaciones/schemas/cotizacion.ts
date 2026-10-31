import { z } from "zod";

const precio = (mensaje: string) =>
  z
    .string()
    .min(1, mensaje)
    .refine(
      (valor) =>
        /^\d+(\.\d{1,2})?$/.test(valor.trim()) &&
        Number.isFinite(Number(valor)) &&
        Number(valor) >= 0,
      { message: "Ingresá un importe válido con hasta 2 decimales." },
    );

export const esquemaDatosCotizacion = z.object({
  id_tipo_vehiculo: z.string().min(1, "Elegí un tipo de vehículo."),
  horas_estimadas: z
    .string()
    .min(1, "Ingresá las horas estimadas.")
    .refine((valor) => Number.isFinite(Number(valor)) && Number(valor) >= 1, {
      message: "Las horas deben ser 1 o más.",
    }),
  km_estimados: z
    .string()
    .min(1, "Ingresá los kilómetros estimados.")
    .refine((valor) => Number.isFinite(Number(valor)) && Number(valor) >= 0, {
      message: "Los kilómetros no pueden ser negativos.",
    }),
  requiere_ayudante: z.boolean().default(false),
  acceso_escalera: z.boolean().default(false),
  zona_concurrida: z.boolean().default(false),
  urgencia_mismo_dia: z.boolean().default(false),
});

export const esquemaCotizacion = esquemaDatosCotizacion.extend({
  precio_acordado: precio("Ingresá el precio final acordado."),
});

export const DATOS_COTIZACION_INICIALES = {
  id_tipo_vehiculo: "",
  horas_estimadas: "1",
  km_estimados: "0",
  requiere_ayudante: false,
  acceso_escalera: false,
  zona_concurrida: false,
  urgencia_mismo_dia: false,
} satisfies z.input<typeof esquemaDatosCotizacion>;

export type EntradaFormularioCotizacion = z.input<typeof esquemaCotizacion>;
export type ValoresFormularioCotizacion = z.output<typeof esquemaCotizacion>;
export type DatosCotizacion = z.input<typeof esquemaDatosCotizacion>;
export type ValoresDatosCotizacion = z.output<typeof esquemaDatosCotizacion>;

export { precio as esquemaPrecioAcordado };
