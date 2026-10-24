import { z } from "zod";

const TELEFONO_DIGITOS_MIN = 7;
const TELEFONO_DIGITOS_MAX = 20;

function contarDigitos(texto: string): number {
  return (texto.match(/\d/g) ?? []).length;
}

export const esquemaChofer = z.object({
  nombre_completo: z
    .string()
    .trim()
    .min(3, "Ingresá el nombre completo.")
    .max(120, "El nombre no puede superar los 120 caracteres."),
  telefono: z
    .string()
    .trim()
    .max(20, "El teléfono no puede superar los 20 caracteres.")
    .refine(
      (valor) => {
        const digitos = contarDigitos(valor);
        return digitos >= TELEFONO_DIGITOS_MIN && digitos <= TELEFONO_DIGITOS_MAX;
      },
      { message: "El teléfono debe tener entre 7 y 20 dígitos." },
    ),
});

export type ValoresChofer = z.input<typeof esquemaChofer>;
export type ChoferValidado = z.output<typeof esquemaChofer>;
