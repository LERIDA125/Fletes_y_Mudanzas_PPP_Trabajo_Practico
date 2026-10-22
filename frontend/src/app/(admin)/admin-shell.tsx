"use client";

import {
  Bell,
  CalendarDays,
  ChevronDown,
  FileText,
  LayoutDashboard,
  Menu,
  PackageCheck,
  Plus,
  ReceiptText,
  Truck,
  UserRound,
  UsersRound,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";

const navItems = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Agenda", href: "/servicios", icon: CalendarDays },
  { label: "Clientes", href: "/clientes", icon: UsersRound },
  { label: "Choferes", href: "/choferes", icon: UserRound },
  { label: "Vehículos", href: "/vehiculos", icon: Truck },
  { label: "Cotizaciones", href: "/servicios", icon: FileText, badge: "4" },
  { label: "Rendiciones", href: "/servicios", icon: ReceiptText },
];

export function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  function esActivo(href: string) {
    if (href === "/") {
      return pathname === "/";
    }
    return pathname.startsWith(href);
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#f7f8fa] text-slate-950">
      {/* Sidebar de escritorio y drawer móvil */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-slate-200 bg-white px-4 py-5 transition-transform lg:translate-x-0 ${
          mobileNavOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between px-3">
          <Link
            href="/servicios"
            className="flex items-center gap-3 transition-opacity hover:opacity-90"
            onClick={() => setMobileNavOpen(false)}
          >
            <div className="flex size-9 items-center justify-center rounded-xl bg-slate-950 text-white shadow-xs">
              <Truck className="size-5" />
            </div>
            <div>
              <p className="text-sm font-bold tracking-tight text-slate-950">MoviFlow</p>
              <p className="text-[11px] text-slate-500">Gestión operativa</p>
            </div>
          </Link>
          <button
            type="button"
            className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 lg:hidden"
            onClick={() => setMobileNavOpen(false)}
            aria-label="Cerrar menú"
          >
            <X className="size-5" />
          </button>
        </div>

        <div className="my-6 h-px bg-slate-200" />

        <nav
          className="flex flex-1 flex-col gap-1 overflow-y-auto"
          aria-label="Navegación principal"
        >
          <p className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
            Menú principal
          </p>
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = esActivo(item.href);

            return (
              <Link
                key={item.label}
                href={item.href}
                aria-current={active ? "page" : undefined}
                onClick={() => setMobileNavOpen(false)}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium transition-colors ${
                  active
                    ? "bg-slate-100 text-slate-950 font-semibold"
                    : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
                }`}
              >
                <Icon
                  className={`size-4 shrink-0 ${active ? "text-slate-950" : "text-slate-400"}`}
                />
                <span className="truncate">{item.label}</span>
                {item.badge ? (
                  <span className="ml-auto rounded-full bg-slate-200 px-2 py-0.5 text-[10px] font-semibold text-slate-600">
                    {item.badge}
                  </span>
                ) : null}
              </Link>
            );
          })}
        </nav>

        {/* Tarjeta inferior informativa */}
        <div className="mt-4 rounded-xl bg-slate-950 p-4 text-white shadow-xs">
          <div className="mb-3 flex size-8 items-center justify-center rounded-lg bg-white/10">
            <PackageCheck className="size-4" />
          </div>
          <p className="text-xs font-semibold">Todo bajo control</p>
          <p className="mt-1 text-[11px] leading-relaxed text-slate-400">
            Organizá tus servicios y equipos desde un solo lugar.
          </p>
        </div>
      </aside>

      {/* Overlay oscuro para móvil */}
      {mobileNavOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-slate-950/20 backdrop-blur-xs lg:hidden"
          aria-label="Cerrar menú"
          onClick={() => setMobileNavOpen(false)}
        />
      ) : null}

      {/* Contenido principal con margen a la izquierda en desktop */}
      <div className="min-h-screen lg:pl-64">
        {/* Top Navbar */}
        <header className="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-slate-200 bg-white/90 px-5 backdrop-blur-md sm:px-8">
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="rounded-lg p-2 text-slate-700 hover:bg-slate-100 lg:hidden"
              onClick={() => setMobileNavOpen(true)}
              aria-label="Abrir menú"
            >
              <Menu className="size-5" />
            </button>
            <div>
              <p className="text-xs text-slate-500">Lunes, 24 de junio de 2024</p>
              <h1 className="text-xl font-bold tracking-tight text-slate-900">
                Buen día, equipo
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            <Link
              href="/servicios"
              className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-sm font-medium text-slate-700 shadow-xs hover:bg-slate-50 transition-colors"
            >
              <Plus className="size-4 text-slate-600" />
              <span>Nuevo Servicio / Cotizar</span>
            </Link>

            <button
              type="button"
              className="relative rounded-lg p-2 text-slate-500 hover:bg-slate-100 transition-colors"
              aria-label="Notificaciones"
            >
              <Bell className="size-5" />
              <span className="absolute right-2 top-2 size-1.5 rounded-full bg-orange-500" />
            </button>

            <div className="hidden h-7 w-px bg-slate-200 sm:block" />

            <div className="flex size-9 items-center justify-center rounded-full bg-orange-100 text-xs font-semibold text-orange-700">
              AM
            </div>
            <div className="hidden text-left sm:block">
              <p className="text-xs font-semibold text-slate-900">Ana Molina</p>
              <p className="text-[11px] text-slate-500">Administradora</p>
            </div>
            <ChevronDown className="hidden size-4 text-slate-400 sm:block" />
          </div>
        </header>

        {/* Área de la página */}
        <main className="mx-auto max-w-[1500px] px-5 py-7 sm:px-8 sm:py-9">
          {children}
        </main>
      </div>
    </div>
  );
}
