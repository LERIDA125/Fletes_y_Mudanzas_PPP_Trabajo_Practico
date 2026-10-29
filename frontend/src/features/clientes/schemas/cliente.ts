import { z } from "zod";

const RAZON_SOCIAL_MIN = 3;
const RAZON_SOCIAL_MAX = 120;
const DIRECCION_MIN = 5;
const DIRECCION_MAX = 250;
const TELEFONO_DIGITOS_MIN = 7;
const TELEFONO_DIGITOS_MAX = 20;
const TELEFONO_MAX = 20;

function contarDigitos(texto: string): number {
  return (texto.match(/\d/g) ?? []).length;
}

export const esquemaCliente = z.object({
  razon_social: z
    .string()
    .trim()
    .min(RAZON_SOCIAL_MIN, "La razón social debe tener al menos 3 caracteres.")
    .max(RAZON_SOCIAL_MAX, "La razón social no puede superar los 120 caracteres."),
  telefono: z
    .string()
    .trim()
    .max(TELEFONO_MAX, "El teléfono no puede superar los 20 caracteres.")
    .refine(
      (valor) => {
        const digitos = contarDigitos(valor);
        return digitos >= TELEFONO_DIGITOS_MIN && digitos <= TELEFONO_DIGITOS_MAX;
      },
      { message: "El teléfono debe tener entre 7 y 20 dígitos." },
    ),
  direccion_habitual: z
    .string()
    .trim()
    .min(DIRECCION_MIN, "La dirección habitual debe tener al menos 5 caracteres.")
    .max(DIRECCION_MAX, "La dirección habitual no puede superar los 250 caracteres."),
  tiene_cuenta_corriente: z.boolean(),
});

export type ValoresCliente = z.input<typeof esquemaCliente>;
export type ClienteValidado = z.output<typeof esquemaCliente>;
