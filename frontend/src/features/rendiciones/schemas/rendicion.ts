import { z } from "zod";

const OBSERVACIONES_MAX = 500;

const importe = (mensaje: string) => z.number({ error: mensaje }).min(0, mensaje);

export const esquemaRendicion = z.object({
  id_servicio: z.number().int().positive("Seleccioná un servicio finalizado."),
  tarifa: importe("Ingresá una tarifa válida."),
  adelanto: importe("Ingresá un adelanto válido."),
  combustible: importe("Ingresá un gasto válido."),
  peajes: importe("Ingresá un gasto válido."),
  otros: importe("Ingresá un gasto válido."),
  observaciones: z
    .string()
    .trim()
    .max(
      OBSERVACIONES_MAX,
      `Las observaciones no pueden superar los ${OBSERVACIONES_MAX} caracteres.`,
    ),
});

export type ValoresRendicion = z.input<typeof esquemaRendicion>;
export type RendicionValidada = z.output<typeof esquemaRendicion>;
