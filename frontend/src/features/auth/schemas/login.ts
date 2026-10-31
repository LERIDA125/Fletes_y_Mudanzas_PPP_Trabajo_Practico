import { z } from "zod";

const USERNAME_MAX = 50;
const PASSWORD_MAX = 128;

export const esquemaLogin = z.object({
  username: z
    .string()
    .trim()
    .min(1, "Ingresá tu usuario.")
    .max(USERNAME_MAX, `El usuario no puede superar los ${USERNAME_MAX} caracteres.`),
  password: z
    .string()
    .min(1, "Ingresá tu contraseña.")
    .max(PASSWORD_MAX, `La contraseña no puede superar los ${PASSWORD_MAX} caracteres.`),
});

export type ValoresLogin = z.input<typeof esquemaLogin>;
