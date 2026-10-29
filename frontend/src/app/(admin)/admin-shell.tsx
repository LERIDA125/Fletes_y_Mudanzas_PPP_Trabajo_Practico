"use client";

import {
  ArrowRight,
  CalendarDays,
  CircleDollarSign,
  Clock3,
  FileText,
  LayoutDashboard,
  Menu,
  Moon,
  PackageCheck,
  Plus,
  Sun,
  Truck,
  UserRound,
  UsersRound,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSyncExternalStore, useState, type ReactNode } from "react";

const navItems = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Agenda", href: "/agenda", icon: CalendarDays },
  { label: "Clientes", href: "/clientes", icon: UsersRound },
  { label: "Choferes", href: "/choferes", icon: UserRound },
  { label: "Vehículos", href: "/vehiculos", icon: Truck },
  { label: "Cotizaciones", href: "/cotizaciones", icon: FileText },
  { label: "Servicios", href: "/servicios", icon: PackageCheck },
  { label: "Rendiciones", href: "/rendiciones", icon: CircleDollarSign },
];

function subscribeTheme(callback: () => void) {
  window.addEventListener("storage", callback);
  const observer = new MutationObserver(callback);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class", "data-theme"],
  });
  return () => {
    window.removeEventListener("storage", callback);
    observer.disconnect();
  };
}

function getThemeSnapshot(): "dark" | "light" {
  if (typeof document === "undefined") return "light";
  return document.documentElement.classList.contains("dark") ||
    document.documentElement.getAttribute("data-theme") === "dark"
    ? "dark"
    : "light";
}

function getServerThemeSnapshot(): "dark" | "light" {
  return "light";
}

export function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const theme = useSyncExternalStore(
    subscribeTheme,
    getThemeSnapshot,
    getServerThemeSnapshot,
  );

  function toggleTheme() {
    const nextTheme = theme === "dark" ? "light" : "dark";
    if (nextTheme === "dark") {
      document.documentElement.classList.add("dark");
      document.documentElement.setAttribute("data-theme", "dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      document.documentElement.setAttribute("data-theme", "light");
      localStorage.setItem("theme", "light");
    }
  }

  function esActivo(href: string) {
    if (href === "/") {
      return pathname === "/";
    }
    return pathname.startsWith(href);
  }

  return (
    <div className="min-h-screen bg-[#f7f9fc] text-[#172b4d] transition-colors duration-150 dark:bg-[#0b1320] dark:text-[#f1f5f9]">
      {/* Sidebar escritorio */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[252px] flex-col border-r border-[#e8edf4] bg-white transition-colors duration-150 lg:flex dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <div className="flex h-[88px] items-center gap-3 border-b border-[#eef1f5] px-7 dark:border-[#1e2c44]">
          <div className="grid size-9 place-items-center rounded-xl bg-[#2165d5] text-white shadow-xs">
            <Truck size={19} strokeWidth={2.5} />
          </div>
          <div>
            <div className="text-[17px] font-bold tracking-[-0.03em] text-[#172b4d] dark:text-white">
              Move<span className="text-[#2165d5] dark:text-[#60a5fa]">ly</span>
            </div>
            <div className="text-[10px] font-medium uppercase tracking-[0.18em] text-[#91a0b5] dark:text-[#64748b]">
              Logística simple
            </div>
          </div>
        </div>

        <nav
          className="flex flex-1 flex-col gap-1 px-4 py-7"
          aria-label="Navegación principal"
        >
          <p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-[#9ba8bb] dark:text-[#64748b]">
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
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-left text-[13px] font-medium transition-colors ${
                  active
                    ? "bg-[#edf4ff] font-semibold text-[#2165d5] dark:bg-[#1e3458] dark:text-[#60a5fa]"
                    : "text-[#718096] hover:bg-[#f6f8fb] hover:text-[#172b4d] dark:text-[#94a3b8] dark:hover:bg-[#18263d] dark:hover:text-white"
                }`}
              >
                <Icon size={17} strokeWidth={active ? 2.4 : 1.8} />
                <span className="truncate">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Tarjeta de soporte */}
        <div className="mx-4 mb-6 rounded-2xl bg-[#f4f8ff] p-4 dark:bg-[#16253d]">
          <p className="text-[12px] font-semibold text-[#2165d5] dark:text-[#60a5fa]">
            ¿Necesitás ayuda?
          </p>
          <p className="mt-1 text-[11px] leading-4 text-[#7e98bc] dark:text-[#94a3b8]">
            Estamos para ayudarte a ordenar tu operación.
          </p>
          <a
            href="mailto:soporte@movely.com"
            className="mt-3 inline-flex items-center text-[11px] font-bold text-[#2165d5] hover:underline dark:text-[#60a5fa]"
          >
            Contactar soporte <ArrowRight className="ml-1 inline" size={12} />
          </a>
        </div>
      </aside>

      {/* Drawer móvil */}
      {mobileNavOpen && (
        <div className="fixed inset-0 z-40 bg-[#172b4d]/40 backdrop-blur-xs lg:hidden">
          <div className="fixed inset-y-0 left-0 w-[260px] border-r border-[#e8edf4] bg-white p-5 shadow-2xl dark:border-[#1e2c44] dark:bg-[#111c2e]">
            <div className="flex items-center justify-between border-b border-[#eef1f5] pb-4 dark:border-[#1e2c44]">
              <div className="flex items-center gap-3">
                <div className="grid size-8 place-items-center rounded-xl bg-[#2165d5] text-white">
                  <Truck size={17} strokeWidth={2.5} />
                </div>
                <div className="text-[16px] font-bold text-[#172b4d] dark:text-white">
                  Move<span className="text-[#2165d5] dark:text-[#60a5fa]">ly</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setMobileNavOpen(false)}
                className="rounded-lg p-1 text-[#8b99ab] hover:bg-[#f3f5f8] dark:hover:bg-[#18263d]"
              >
                <X size={18} />
              </button>
            </div>

            <nav className="mt-5 flex flex-col gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = esActivo(item.href);
                return (
                  <Link
                    key={item.label}
                    href={item.href}
                    onClick={() => setMobileNavOpen(false)}
                    className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                      active
                        ? "bg-[#edf4ff] font-semibold text-[#2165d5]"
                        : "text-[#718096] hover:bg-[#f6f8fb] dark:text-[#94a3b8] dark:hover:bg-[#18263d]"
                    }`}
                  >
                    <Icon size={17} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      )}

      {/* Contenedor principal */}
      <div className="lg:pl-[252px]">
        {/* Header superior */}
        <header className="sticky top-0 z-20 flex h-[88px] items-center justify-between border-b border-[#e8edf4] bg-white/95 px-5 backdrop-blur-md transition-colors duration-150 sm:px-8 lg:px-10 dark:border-[#1e2c44] dark:bg-[#111c2e]/95">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileNavOpen(true)}
              className="mr-2 rounded-lg p-2 text-[#718096] hover:bg-[#f3f5f8] lg:hidden dark:text-[#94a3b8] dark:hover:bg-[#18263d]"
              aria-label="Abrir menú"
            >
              <Menu size={21} />
            </button>
            <div className="min-w-0">
              <p className="truncate text-xs text-[#8d9bb0] dark:text-[#94a3b8]">
                Martes, 23 de septiembre de 2026
              </p>
              <h1 className="mt-0.5 truncate text-lg font-bold tracking-tight text-[#172b4d] sm:text-xl dark:text-white">
                Operaciones Fletes y Mudanzas
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-2.5 sm:gap-3">
            {/* Botón selector Modo Oscuro / Modo Claro */}
            <button
              type="button"
              onClick={toggleTheme}
              className="grid size-9 place-items-center rounded-xl border border-[#e5eaf1] bg-[#fafcff] text-[#5f7087] transition hover:bg-[#edf4ff] hover:text-[#2165d5] dark:border-[#1e2c44] dark:bg-[#16253d] dark:text-[#94a3b8] dark:hover:text-[#60a5fa]"
              aria-label={
                theme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro"
              }
              title={theme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}
            >
              {theme === "dark" ? (
                <Sun size={17} className="text-amber-400" />
              ) : (
                <Moon size={17} />
              )}
            </button>

            <div className="hidden items-center gap-2 rounded-xl border border-[#e5eaf1] bg-[#fafcff] px-3 py-2 text-xs font-semibold text-[#5f7087] sm:flex dark:border-[#1e2c44] dark:bg-[#16253d] dark:text-[#cbd5e1]">
              <Clock3 size={14} className="text-[#2165d5] dark:text-[#60a5fa]" />
              <span>Sincronizado ahora</span>
            </div>

            <Link
              href="/cotizaciones"
              className="hidden sm:flex items-center gap-1.5 rounded-xl bg-[#2165d5] px-3.5 py-2 text-xs font-bold text-white shadow-[0_4px_10px_rgba(33,101,213,0.18)] hover:bg-[#1857bd] dark:bg-[#2563eb] dark:hover:bg-[#1d4ed8]"
            >
              <Plus size={15} />
              <span>Cotizar servicio</span>
            </Link>

            <div className="grid size-9 place-items-center rounded-full bg-[#dbe9ff] text-xs font-bold text-[#2165d5] dark:bg-[#1e3a66] dark:text-[#93c5fd]">
              FG
            </div>
          </div>
        </header>

        {/* Área de la página */}
        <main className="mx-auto max-w-[1440px] px-5 py-7 sm:px-8 lg:px-10">
          {children}
        </main>
      </div>
    </div>
  );
}
