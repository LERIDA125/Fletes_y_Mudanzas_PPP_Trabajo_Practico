import { PackageCheck, ShieldCheck, Truck } from "lucide-react";
import { redirect } from "next/navigation";

import { FormularioLogin } from "@/features/auth/components/formulario-login";
import { ErrorApi } from "@/lib/api/http";
import { obtenerUsuarioActual } from "@/lib/auth/guards";
import { rutaInicialPorRol } from "@/lib/auth/rutas";
import type { UsuarioSesion } from "@/lib/auth/tipos";

export const instant = false;

export const metadata = {
  title: "Iniciar sesión",
  description: "Acceso al sistema de gestión de Fletes y Mudanzas Express.",
};

export default async function LoginPage() {
  let usuario: UsuarioSesion | null = null;

  try {
    usuario = await obtenerUsuarioActual();
  } catch (error) {
    // Si la API no responde, mostramos el formulario en vez de asumir sesión.
    if (!(error instanceof ErrorApi)) {
      throw error;
    }
  }

  if (usuario) {
    redirect(rutaInicialPorRol(usuario.rol));
  }

  return (
    <main className="grid min-h-screen grid-cols-1 bg-[#f7f9fc] dark:bg-[#0b1320] lg:grid-cols-[1.05fr_1fr]">
      <section className="relative hidden overflow-hidden bg-gradient-to-br from-[#172b4d] via-[#1d3f78] to-[#2165d5] p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div
          aria-hidden="true"
          className="absolute -top-28 -right-24 size-[420px] rounded-full border border-white/10 bg-white/5"
        />
        <div
          aria-hidden="true"
          className="absolute -bottom-32 -left-20 size-[380px] rounded-full border border-white/10 bg-white/5"
        />

        <div className="relative flex items-center gap-3">
          <div className="grid size-11 place-items-center rounded-2xl bg-white/15 ring-1 ring-white/20">
            <Truck size={22} strokeWidth={2.4} />
          </div>
          <div>
            <p className="text-xl font-bold tracking-[-0.03em]">
              Move<span className="text-[#93c5fd]">ly</span>
            </p>
            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-white/60">
              Fletes y mudanzas
            </p>
          </div>
        </div>

        <div className="relative max-w-md">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#93c5fd]">
            Operación centralizada
          </p>
          <h1 className="mt-3 text-4xl font-bold leading-[1.1] tracking-tight">
            Todo tu día de trabajo, en un solo lugar.
          </h1>
          <p className="mt-4 text-sm leading-6 text-white/70">
            Servicios, agenda, clientes, choferes y rendiciones. La operación de Fletes y
            Mudanzas Express sin planillas sueltas.
          </p>

          <ul className="mt-8 flex flex-col gap-3 text-sm text-white/80">
            <li className="flex items-center gap-2.5">
              <PackageCheck size={17} className="text-[#93c5fd]" />
              Seguimiento de cada servicio de punta a punta.
            </li>
            <li className="flex items-center gap-2.5">
              <ShieldCheck size={17} className="text-[#93c5fd]" />
              Acceso protegido según el rol de cada cuenta.
            </li>
          </ul>
        </div>

        <p className="relative text-xs text-white/45">
          © {new Date().getFullYear()} Fletes y Mudanzas Express
        </p>
      </section>

      <section className="flex items-center justify-center px-5 py-12 sm:px-10">
        <div className="w-full max-w-md">
          <div className="mb-8 flex items-center gap-3 lg:hidden">
            <div className="grid size-10 place-items-center rounded-xl bg-[#2165d5] text-white shadow-md">
              <Truck size={20} strokeWidth={2.4} />
            </div>
            <div>
              <p className="text-lg font-bold tracking-[-0.03em] text-[#172b4d] dark:text-white">
                Move<span className="text-[#2165d5] dark:text-[#60a5fa]">ly</span>
              </p>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#91a0b5] dark:text-[#64748b]">
                Fletes y mudanzas
              </p>
            </div>
          </div>

          <div className="rounded-3xl border border-[#e8edf4] bg-white p-7 shadow-[0_24px_60px_-30px_rgba(15,35,70,0.35)] sm:p-9 dark:border-[#1e2c44] dark:bg-[#111c2e]">
            <div className="mb-7">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#2165d5] dark:text-[#60a5fa]">
                Acceso al sistema
              </p>
              <h2 className="mt-2 text-2xl font-bold tracking-tight text-[#172b4d] dark:text-white">
                Iniciá sesión
              </h2>
              <p className="mt-1.5 text-sm text-[#7f8da1] dark:text-[#94a3b8]">
                Usá las credenciales que te asignó un administrador.
              </p>
            </div>

            <FormularioLogin />
          </div>

          <p className="mt-6 text-center text-xs text-[#8b99ab] dark:text-[#64748b]">
            Acceso restringido al personal autorizado.
          </p>
        </div>
      </section>
    </main>
  );
}
