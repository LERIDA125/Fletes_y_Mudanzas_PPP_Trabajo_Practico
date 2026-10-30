import { CheckCircle2, Truck } from "lucide-react";

import { BotonCerrarSesion } from "@/features/auth/components/boton-cerrar-sesion";
import { requestAutenticado } from "@/lib/api/servidor";
import { exigirRol } from "@/lib/auth/guards";
import type { components } from "@/types/openapi";

export const instant = false;

export const metadata = {
  title: "Inicio del chofer",
  description: "Estado de la cuenta del chofer en Fletes y Mudanzas Express.",
};

export default async function ChoferDashboardPage() {
  const usuario = await exigirRol("CHOFER");

  let nombre = usuario.username;

  if (usuario.id_chofer) {
    try {
      const chofer = await requestAutenticado<components["schemas"]["ChoferRead"]>(
        `/api/choferes/${usuario.id_chofer}`,
      );
      if (chofer?.nombre_completo) {
        nombre = chofer.nombre_completo;
      }
    } catch {
      // Si el detalle no responde, el username sigue siendo una identificación válida.
    }
  }

  return (
    <main className="min-h-screen bg-[#f7f9fc] text-[#172b4d] dark:bg-[#0b1320] dark:text-[#f1f5f9]">
      <header className="border-b border-[#e8edf4] bg-white/95 dark:border-[#1e2c44] dark:bg-[#111c2e]/95">
        <div className="mx-auto flex h-[76px] max-w-4xl items-center justify-between px-5 sm:px-8">
          <div className="flex items-center gap-3">
            <div className="grid size-9 place-items-center rounded-xl bg-[#2165d5] text-white shadow-xs">
              <Truck size={19} strokeWidth={2.5} />
            </div>
            <div>
              <p className="text-[17px] font-bold tracking-[-0.03em]">
                Move<span className="text-[#2165d5] dark:text-[#60a5fa]">ly</span>
              </p>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[#91a0b5] dark:text-[#64748b]">
                Fletes y mudanzas
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden flex-col items-end sm:flex">
              <span className="text-xs font-semibold">{usuario.username}</span>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-[#91a0b5] dark:text-[#64748b]">
                Chofer
              </span>
            </div>
            <BotonCerrarSesion />
          </div>
        </div>
      </header>

      <section className="mx-auto flex max-w-4xl flex-col gap-6 px-5 py-12 sm:px-8">
        <div className="rounded-3xl border border-[#e8edf4] bg-white p-8 shadow-[0_24px_60px_-34px_rgba(15,35,70,0.3)] sm:p-10 dark:border-[#1e2c44] dark:bg-[#111c2e]">
          <div className="grid size-12 place-items-center rounded-2xl bg-[#e9f8ef] text-[#248952] dark:bg-[#143324] dark:text-[#4ade80]">
            <CheckCircle2 aria-hidden="true" size={24} />
          </div>

          <p className="mt-6 text-xs font-semibold uppercase tracking-[0.18em] text-[#2165d5] dark:text-[#60a5fa]">
            Cuenta habilitada
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Bienvenido, {nombre}.
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-6 text-[#7f8da1] dark:text-[#94a3b8]">
            Tu cuenta está activa. Próximamente verás tus viajes asignados aquí.
          </p>

          <div className="mt-8 inline-flex items-center gap-2 rounded-full bg-[#f4f8ff] px-3.5 py-1.5 text-xs font-semibold text-[#2165d5] dark:bg-[#16253d] dark:text-[#93c5fd]">
            <Truck aria-hidden="true" size={14} />
            Sin viajes asignados por ahora
          </div>
        </div>

        <p className="text-center text-xs text-[#8b99ab] dark:text-[#64748b]">
          Este espacio se habilitará cuando esté disponible la operación del chofer.
        </p>
      </section>
    </main>
  );
}
