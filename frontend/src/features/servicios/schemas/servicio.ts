import { z } from "zod";

const TELEFONO_DIGITOS_MIN = 7;
const TELEFONO_DIGITOS_MAX = 20;

function contarDigitos(texto: string): number {
  return (texto.match(/\d/g) ?? []).length;
}

export const esquemaFormularioServicio = z
  .object({
    modo_cliente: z.enum(["existente", "nuevo"]).default("existente"),
    id_cliente: z.string(),
    razon_social: z.string(),
    telefono: z.string(),
    direccion_habitual: z.string(),
    tiene_cuenta_corriente: z.boolean().default(false),
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
    id_chofer: z.string(),
    id_vehiculo: z.string(),
  })
  .superRefine((valores, ctx) => {
    if (valores.modo_cliente === "existente") {
      if (!valores.id_cliente) {
        ctx.addIssue({
          code: "custom",
          path: ["id_cliente"],
          message: "Elegí un cliente.",
        });
      }
      return;
    }

    const razonSocial = valores.razon_social.trim();
    if (razonSocial.length < 2) {
      ctx.addIssue({
        code: "custom",
        path: ["razon_social"],
        message: "Ingresá la razón social del cliente.",
      });
    }

    const telefono = valores.telefono.trim();
    const digitos = contarDigitos(telefono);
    if (
      telefono.length > 20 ||
      digitos < TELEFONO_DIGITOS_MIN ||
      digitos > TELEFONO_DIGITOS_MAX
    ) {
      ctx.addIssue({
        code: "custom",
        path: ["telefono"],
        message: "El teléfono debe tener entre 7 y 20 dígitos.",
      });
    }

    if (valores.direccion_habitual.trim().length < 2) {
      ctx.addIssue({
        code: "custom",
        path: ["direccion_habitual"],
        message: "Ingresá la dirección habitual del cliente.",
      });
    }
  });

// `modo_cliente` y `tiene_cuenta_corriente` tienen `default`, así que la
// entrada del esquema los admite ausentes y la salida los garantiza.
// `zodResolver` devuelve un `Resolver<input, ctx, output>`: RHF necesita los
// dos tipos para que `trigger()` y `getValues()` sean consistentes.
export type EntradaFormularioServicio = z.input<typeof esquemaFormularioServicio>;
export type ValoresFormularioServicio = z.output<typeof esquemaFormularioServicio>;
