import { ShieldCheck, UserPlus } from "lucide-react";

import { FormularioCrearUsuario } from "@/features/usuarios/components/formulario-crear-usuario";
import { listarChoferesActivos } from "@/lib/api/choferes";
import { ErrorApi } from "@/lib/api/http";
import type { Chofer } from "@/features/choferes/types";

export const instant = false;

export const metadata = {
  title: "Usuarios",
  description: "Alta de cuentas de administrador y chofer.",
};

export default async function UsuariosPage() {
  let choferes: Chofer[] = [];
  let errorChoferes = "";

  try {
    choferes = await listarChoferesActivos();
  } catch (error) {
    if (error instanceof ErrorApi) {
      errorChoferes =
        "No pudimos cargar los choferes activos. Las cuentas ADMIN se pueden crear igual.";
    } else {
      throw error;
    }
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
            Administración
          </p>
          <h2 className="flex items-center gap-2 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            <UserPlus
              aria-hidden="true"
              size={26}
              className="text-[#2165d5] dark:text-[#60a5fa]"
            />
            Crear usuario
          </h2>
          <p className="mt-1 text-xs text-[#7f8da1] dark:text-[#94a3b8]">
            Da de alta una cuenta ADMIN o una cuenta CHOFER vinculada a un chofer activo.
          </p>
        </div>

        <div className="inline-flex items-center gap-2 self-start rounded-full bg-[#edf4ff] px-3 py-1.5 text-[11px] font-semibold text-[#2165d5] dark:bg-[#1e3458] dark:text-[#93c5fd]">
          <ShieldCheck aria-hidden="true" size={14} />
          Solo administradores
        </div>
      </div>

      <section className="rounded-2xl border border-[#e8edf4] bg-white p-6 shadow-sm sm:p-8 dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <div className="mb-6 border-b border-[#edf0f4] pb-5 dark:border-[#1e2c44]">
          <h3 className="text-base font-bold text-[#172b4d] dark:text-white">
            Datos de la cuenta
          </h3>
          <p className="mt-0.5 text-xs text-[#96a2b2] dark:text-[#94a3b8]">
            La contraseña se guarda como hash Argon2id y nunca se vuelve a mostrar.
          </p>
        </div>

        {errorChoferes ? (
          <p
            role="alert"
            className="mb-5 rounded-xl border border-amber-200 bg-amber-50 px-3.5 py-2.5 text-sm font-medium text-amber-800 dark:border-amber-900/60 dark:bg-amber-950/40 dark:text-amber-300"
          >
            {errorChoferes}
          </p>
        ) : null}

        <FormularioCrearUsuario choferes={choferes} />
      </section>

      <p className="text-center text-xs text-[#8b99ab] dark:text-[#64748b]">
        Las cuentas CHOFER requieren un chofer activo que todavía no tenga otra cuenta.
      </p>
    </div>
  );
}
