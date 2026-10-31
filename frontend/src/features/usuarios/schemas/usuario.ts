import { z } from "zod";

export const ROLES_USUARIO = ["ADMIN", "CHOFER"] as const;

export type RolUsuario = (typeof ROLES_USUARIO)[number];

const USERNAME_MIN = 3;
const USERNAME_MAX = 50;
const PASSWORD_MIN = 12;
const PASSWORD_MAX = 128;

export const esquemaUsuario = z
  .object({
    username: z
      .string()
      .trim()
      .min(USERNAME_MIN, `El usuario debe tener al menos ${USERNAME_MIN} caracteres.`)
      .max(USERNAME_MAX, `El usuario no puede superar los ${USERNAME_MAX} caracteres.`),
    password: z
      .string()
      .min(PASSWORD_MIN, `La contraseña debe tener al menos ${PASSWORD_MIN} caracteres.`)
      .max(
        PASSWORD_MAX,
        `La contraseña no puede superar los ${PASSWORD_MAX} caracteres.`,
      ),
    rol: z.enum(ROLES_USUARIO),
    id_chofer: z.number().int().positive().nullable().optional(),
  })
  .superRefine((valores, ctx) => {
    if (valores.rol === "CHOFER" && !valores.id_chofer) {
      ctx.addIssue({
        code: "custom",
        path: ["id_chofer"],
        message: "Elegí el chofer que usará esta cuenta.",
      });
    }

    if (valores.password.toLowerCase() === valores.username.trim().toLowerCase()) {
      ctx.addIssue({
        code: "custom",
        path: ["password"],
        message: "La contraseña no puede ser igual al nombre de usuario.",
      });
    }
  });

export type ValoresUsuario = z.input<typeof esquemaUsuario>;
export type UsuarioValidado = z.output<typeof esquemaUsuario>;
