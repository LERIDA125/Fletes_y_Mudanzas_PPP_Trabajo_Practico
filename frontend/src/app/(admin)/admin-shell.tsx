"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const NAVEGACION = [
  { href: "/", etiqueta: "Clientes", icono: "groups" },
  { href: "/choferes", etiqueta: "Choferes", icono: "driver" },
  { href: "/vehiculos", etiqueta: "Vehículos", icono: "vehicle" },
  { href: "/servicios", etiqueta: "Servicios", icono: "truck" },
] as const;

type IconoNombre = (typeof NAVEGACION)[number]["icono"];

export function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  const seccionActual =
    NAVEGACION.find((item) =>
      item.href === "/" ? pathname === "/" : pathname.startsWith(item.href),
    )?.etiqueta ?? "Operaciones";

  return (
    <div className="flex min-h-screen bg-[#f8f9ff] text-[#0b1c30]">
      {/* Sidebar de navegación izquierda */}
      <aside className="hidden w-64 shrink-0 flex-col border-r border-[#c6c6cd]/50 bg-white px-3 py-4 md:flex">
        <Link
          href="/"
          className="flex items-center gap-3 border-b border-[#c6c6cd]/40 px-2 pb-4 transition-opacity hover:opacity-90"
        >
          <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-[#131b2e] text-white shadow-xs">
            <Icono nombre="truck" className="size-5" />
          </span>
          <span className="min-w-0">
            <span className="block truncate text-sm font-bold text-[#0b1c30]">
              Fletes y Mudanzas
            </span>
            <span className="block truncate text-xs text-[#545f73]">
              Operaciones Express
            </span>
          </span>
        </Link>

        <nav aria-label="Secciones" className="mt-5 flex flex-col gap-1.5">
          {NAVEGACION.map((item) => {
            const activo =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={activo ? "page" : undefined}
                className={`flex items-center gap-3 rounded-lg border-l-2 px-3 py-2.5 text-sm font-medium transition-colors ${
                  activo
                    ? "border-[#131b2e] bg-[#eff4ff] text-[#131b2e] font-semibold"
                    : "border-transparent text-[#545f73] hover:bg-[#eff4ff]/60 hover:text-[#0b1c30]"
                }`}
              >
                <Icono nombre={item.icono} className="size-5" />
                <span>{item.etiqueta}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto border-t border-[#c6c6cd]/40 px-2 pt-4 text-xs font-medium text-[#545f73]/80">
          Panel de administración
        </div>
      </aside>

      {/* Área principal */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top Navbar */}
        <header className="sticky top-0 z-20 flex min-h-14 items-center justify-between gap-4 border-b border-[#c6c6cd]/50 bg-white px-6">
          <div className="flex min-w-0 items-center gap-2 text-sm text-[#545f73]">
            <span>Operaciones</span>
            <span aria-hidden="true" className="text-[#c6c6cd]">
              /
            </span>
            <span className="font-bold text-[#0b1c30]">{seccionActual}</span>
          </div>
          <span className="text-xs font-medium text-[#545f73]/80">
            Fletes y Mudanzas Express
          </span>
        </header>

        {/* Navegación móvil */}
        <nav
          aria-label="Secciones móvil"
          className="flex gap-1 overflow-x-auto border-b border-[#c6c6cd]/50 bg-white px-4 py-2 md:hidden"
        >
          {NAVEGACION.map((item) => {
            const activo =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={activo ? "page" : undefined}
                className={`inline-flex min-h-9 shrink-0 items-center gap-2 rounded-md px-3 text-sm font-medium ${
                  activo
                    ? "bg-[#eff4ff] text-[#131b2e] font-semibold"
                    : "text-[#545f73] hover:bg-[#eff4ff]"
                }`}
              >
                <Icono nombre={item.icono} className="size-4" />
                {item.etiqueta}
              </Link>
            );
          })}
        </nav>

        {/* Contenido principal */}
        <main className="mx-auto flex w-full max-w-[1400px] flex-1 flex-col gap-6 p-6 sm:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}

function Icono({ nombre, className }: { nombre: IconoNombre; className?: string }) {
  const paths = {
    groups: (
      <>
        <path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="10" cy="7" r="4" />
        <path d="M20 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
      </>
    ),
    driver: (
      <>
        <circle cx="12" cy="8" r="4" />
        <path d="M5 21a7 7 0 0 1 14 0M19 8h3m-1.5-1.5v3" />
      </>
    ),
    vehicle: (
      <>
        <path d="M3 7h11v11H3zM14 11h4l3 3v4h-7z" />
        <circle cx="7.5" cy="18.5" r="1.5" />
        <circle cx="17.5" cy="18.5" r="1.5" />
      </>
    ),
    truck: (
      <>
        <path d="M3 6h12v12H3zM15 10h4l3 4v4h-7z" />
        <circle cx="7.5" cy="18.5" r="1.5" />
        <circle cx="18.5" cy="18.5" r="1.5" />
      </>
    ),
  };
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.7"
      viewBox="0 0 24 24"
    >
      {paths[nombre]}
    </svg>
  );
}
