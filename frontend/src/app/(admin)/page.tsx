"use client";

import {
  ArrowRight,
  CalendarDays,
  CircleDollarSign,
  FileText,
  Plus,
  Truck,
  UserRound,
} from "lucide-react";
import Link from "next/link";

const services = [
  {
    time: "08:30",
    client: "María González",
    from: "Palermo",
    to: "Nordelta",
    driver: "Carlos Méndez",
    vehicle: "Grande",
    status: "En curso",
  },
  {
    time: "10:00",
    client: "Estudio Norte",
    from: "Belgrano",
    to: "San Isidro",
    driver: "Lucía Fernández",
    vehicle: "Chico",
    status: "Pendiente",
  },
  {
    time: "11:30",
    client: "Tomás Rivas",
    from: "Villa Urquiza",
    to: "Colegiales",
    driver: "—",
    vehicle: "Grande",
    status: "Pendiente",
  },
  {
    time: "14:00",
    client: "Ana López",
    from: "Caballito",
    to: "Vicente López",
    driver: "Diego Soto",
    vehicle: "Chico",
    status: "Finalizado",
  },
];

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    "En curso": "bg-[#e9f4ff] text-[#2879bd] dark:bg-[#152e4d] dark:text-[#60a5fa]",
    Pendiente: "bg-[#fff4e5] text-[#b86a16] dark:bg-[#3d2914] dark:text-[#fbbf24]",
    Finalizado: "bg-[#e9f8ef] text-[#248952] dark:bg-[#143324] dark:text-[#4ade80]",
  };
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold ${
        styles[status] ??
        "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
      }`}
    >
      {status}
    </span>
  );
}

export default function DashboardPage() {
  const kpis = [
    {
      label: "Servicios del día",
      value: "8",
      note: "+2 vs. ayer",
      icon: CalendarDays,
      tone: "blue",
    },
    {
      label: "Choferes disponibles",
      value: "3",
      note: "de 6 en total",
      icon: UserRound,
      tone: "green",
    },
    {
      label: "Dinero por cobrar hoy",
      value: "$150.000",
      note: "4 servicios pendientes",
      icon: CircleDollarSign,
      tone: "orange",
    },
    {
      label: "Pendiente de rendición",
      value: "$50.000",
      note: "2 rendiciones abiertas",
      icon: FileText,
      tone: "purple",
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
            Resumen operativo
          </p>
          <h2 className="text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            Hola, Federico
          </h2>
          <p className="mt-1 text-xs text-[#7f8da1] dark:text-[#94a3b8]">
            Acá está el resumen de tu operación de hoy.
          </p>
        </div>

        <Link
          href="/servicios"
          className="flex shrink-0 items-center gap-2 rounded-xl bg-[#2165d5] px-4 py-2.5 text-xs font-bold text-white shadow-[0_5px_12px_rgba(33,101,213,0.18)] transition hover:bg-[#1857bd] dark:bg-[#2563eb] dark:hover:bg-[#1d4ed8]"
        >
          <Plus size={16} />
          <span>Nuevo servicio</span>
        </Link>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map(({ label, value, note, icon: Icon, tone }) => (
          <div
            key={label}
            className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]"
          >
            <div className="flex items-start justify-between">
              <p className="text-xs font-medium text-[#8492a6] dark:text-[#94a3b8]">
                {label}
              </p>
              <div
                className={`grid size-8 place-items-center rounded-lg ${
                  tone === "blue"
                    ? "bg-[#edf4ff] text-[#2165d5] dark:bg-[#1a3356] dark:text-[#60a5fa]"
                    : tone === "green"
                      ? "bg-[#e9f8ef] text-[#248952] dark:bg-[#163827] dark:text-[#4ade80]"
                      : tone === "orange"
                        ? "bg-[#fff4e5] text-[#b86a16] dark:bg-[#3d2914] dark:text-[#fbbf24]"
                        : "bg-[#f1edff] text-[#7951c9] dark:bg-[#2b1f48] dark:text-[#c084fc]"
                }`}
              >
                <Icon size={16} />
              </div>
            </div>
            <p className="mt-3 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
              {value}
            </p>
            <p className="mt-1 text-xs text-[#8b99ab] dark:text-[#64748b]">{note}</p>
          </div>
        ))}
      </div>

      {/* Próximos servicios */}
      <section className="rounded-2xl border border-[#e8edf4] bg-white shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <div className="flex items-center justify-between border-b border-[#edf0f4] px-5 py-5 sm:px-6 dark:border-[#1e2c44]">
          <div>
            <h3 className="text-base font-bold text-[#172b4d] dark:text-white">
              Próximos servicios
            </h3>
            <p className="mt-0.5 text-xs text-[#96a2b2] dark:text-[#94a3b8]">
              Los servicios de tu operación para hoy
            </p>
          </div>
          <Link
            href="/agenda"
            className="text-xs font-bold text-[#2165d5] hover:underline dark:text-[#60a5fa]"
          >
            Ver agenda <ArrowRight className="ml-1 inline" size={13} />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-xs">
            <thead>
              <tr className="border-b border-[#f0f2f5] text-[10px] font-bold uppercase tracking-wider text-[#a0adbd] dark:border-[#1e2c44] dark:text-[#64748b]">
                {[
                  "Horario",
                  "Cliente",
                  "Origen",
                  "Destino",
                  "Chofer asignado",
                  "Vehículo",
                  "Estado",
                ].map((head) => (
                  <th key={head} className="px-5 py-3.5 font-bold sm:px-6">
                    {head}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {services.map((service) => (
                <tr
                  key={service.time}
                  className="border-b border-[#f1f3f6] text-xs transition hover:bg-[#fafcff] last:border-0 dark:border-[#1e2c44] dark:hover:bg-[#16253d]"
                >
                  <td className="px-5 py-4 font-bold text-[#172b4d] sm:px-6 dark:text-white">
                    {service.time}
                  </td>
                  <td className="px-5 py-4 font-semibold text-[#172b4d] sm:px-6 dark:text-white">
                    {service.client}
                  </td>
                  <td className="px-5 py-4 text-[#77869a] sm:px-6 dark:text-[#94a3b8]">
                    {service.from}
                  </td>
                  <td className="px-5 py-4 text-[#77869a] sm:px-6 dark:text-[#94a3b8]">
                    {service.to}
                  </td>
                  <td className="px-5 py-4 text-[#5c6d83] sm:px-6 dark:text-[#cbd5e1]">
                    {service.driver}
                  </td>
                  <td className="px-5 py-4 text-[#5c6d83] sm:px-6 dark:text-[#cbd5e1]">
                    <span className="inline-flex items-center gap-1.5">
                      <Truck size={13} className="text-[#9aa7b7] dark:text-[#64748b]" />
                      Camión {service.vehicle.toLowerCase()}
                    </span>
                  </td>
                  <td className="px-5 py-4 sm:px-6">
                    <StatusBadge status={service.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
