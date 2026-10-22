"use client";

import { ChevronLeft, ChevronRight, MapPin, Plus, Truck, UserRound } from "lucide-react";
import { useState } from "react";

const services = [
  {
    time: "08:30",
    client: "María González",
    from: "Palermo, CABA",
    to: "Nordelta, Tigre",
    driver: "Lucas Ramírez",
    vehicle: "Furgón Grande",
    status: "En curso",
    color: "bg-[#2165d5]",
  },
  {
    time: "10:00",
    client: "Estudio Norte",
    from: "Belgrano, CABA",
    to: "Vicente López",
    driver: "Sofía Martínez",
    vehicle: "Camioneta Chica",
    status: "Pendiente",
    color: "bg-[#f0a04b]",
  },
  {
    time: "11:30",
    client: "Tomás Rivas",
    from: "Villa Urquiza",
    to: "Colegiales",
    driver: "Diego Acosta",
    vehicle: "Furgón Grande",
    status: "Pendiente",
    color: "bg-[#f0a04b]",
  },
  {
    time: "14:00",
    client: "Ana López",
    from: "Caballito, CABA",
    to: "Vicente López",
    driver: "Martín Soto",
    vehicle: "Camioneta Chica",
    status: "Finalizado",
    color: "bg-[#248952]",
  },
  {
    time: "16:30",
    client: "Valentina Ruiz",
    from: "Caballito, CABA",
    to: "Haedo, Morón",
    driver: "Esteban Quiroga",
    vehicle: "Furgón Grande",
    status: "Pendiente",
    color: "bg-[#f0a04b]",
  },
];

const monthDays = Array.from({ length: 31 }, (_, i) => ({
  day: i + 1,
  weekday: ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"][i % 7],
  services: i % 5 === 0 ? 2 : i % 3 === 0 ? 1 : 0,
}));

export default function PaginaAgenda() {
  const [selectedDay, setSelectedDay] = useState(23);
  const [month, setMonth] = useState(9);
  const [modalNuevoTurno, setModalNuevoTurno] = useState(false);

  const monthNames = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5]">
            Planificación operativa
          </p>
          <h2 className="text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl">
            Agenda
          </h2>
          <p className="mt-1 text-xs text-[#7f8da1]">
            Visualizá y organizá todos los servicios del mes.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setModalNuevoTurno(true)}
          className="flex shrink-0 items-center gap-2 rounded-xl bg-[#2165d5] px-4 py-2.5 text-xs font-bold text-white shadow-[0_5px_12px_rgba(33,101,213,0.18)] transition hover:bg-[#1857bd]"
        >
          <Plus size={16} />
          <span>Nuevo turno</span>
        </button>
      </div>

      {/* Grid principal: Calendario mensual + Turnos del día */}
      <div className="grid gap-6 xl:grid-cols-[1fr_340px]">
        {/* Calendario mensual */}
        <section className="rounded-2xl border border-[#e8edf4] bg-white p-5 sm:p-6 shadow-sm">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-bold text-[#172b4d]">Agenda operativa</h3>
              <p className="mt-0.5 text-xs text-[#96a2b2]">
                Todos los turnos asignados y libres · vista mensual
              </p>
            </div>

            <div className="flex items-center gap-1 rounded-lg border border-[#e8edf4] bg-[#fcfdfe] p-1">
              <button
                type="button"
                onClick={() => setMonth((prev) => Math.max(1, prev - 1))}
                className="rounded-md p-1.5 text-[#7f8da1] hover:bg-[#f4f7fb]"
                aria-label="Mes anterior"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="min-w-[130px] text-center text-xs font-bold text-[#172b4d]">
                {monthNames[month - 1]} 2026
              </span>
              <button
                type="button"
                onClick={() => setMonth((prev) => Math.min(12, prev + 1))}
                className="rounded-md p-1.5 text-[#7f8da1] hover:bg-[#f4f7fb]"
                aria-label="Mes siguiente"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>

          {/* Leyenda */}
          <div className="mb-5 flex flex-wrap gap-4 text-xs text-[#76869a]">
            <span className="inline-flex items-center">
              <i className="mr-1.5 inline-block size-2.5 rounded-full bg-[#2165d5]" />
              Turno asignado
            </span>
            <span className="inline-flex items-center">
              <i className="mr-1.5 inline-block size-2.5 rounded-full bg-[#e7ebf1]" />
              Día libre
            </span>
            <span className="inline-flex items-center">
              <i className="mr-1.5 inline-block size-2.5 rounded-full bg-[#f0a04b]" />
              Pendiente de confirmar
            </span>
          </div>

          {/* Días del mes */}
          <div className="grid grid-cols-7 gap-2">
            {monthDays.map(({ day, weekday, services: count }) => {
              const isSelected = day === selectedDay;
              return (
                <button
                  type="button"
                  key={day}
                  onClick={() => setSelectedDay(day)}
                  className={`min-h-[96px] rounded-xl border p-2.5 text-left transition-all ${
                    isSelected
                      ? "border-[#2165d5] bg-[#f4f8ff] ring-2 ring-[#2165d5]/20 shadow-sm"
                      : "border-[#edf0f4] bg-white hover:border-[#9bbcf1] hover:bg-[#fafcff]"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-medium text-[#9aa7b7]">
                      {weekday}
                    </span>
                    <span
                      className={`grid size-6 place-items-center rounded-full text-xs font-bold ${
                        isSelected ? "bg-[#2165d5] text-white" : "text-[#53657d]"
                      }`}
                    >
                      {day}
                    </span>
                  </div>

                  {count > 0 ? (
                    <div className="mt-3.5 rounded-md bg-[#edf4ff] px-2 py-1 text-[10px] font-semibold text-[#2165d5]">
                      {count} {count === 1 ? "servicio" : "servicios"}
                    </div>
                  ) : (
                    <div className="mt-4 text-center text-[10px] font-medium text-[#c1c9d4]">
                      Libre
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </section>

        {/* Panel lateral: Turnos del día seleccionado */}
        <aside className="flex flex-col gap-5 rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between border-b border-[#edf0f4] pb-4">
            <div>
              <h3 className="text-base font-bold text-[#172b4d]">Turnos de hoy</h3>
              <p className="mt-0.5 text-xs text-[#96a2b2]">
                Día {selectedDay} de {monthNames[month - 1].toLowerCase()}
              </p>
            </div>
            <span className="rounded-full bg-[#edf4ff] px-2.5 py-1 text-xs font-bold text-[#2165d5]">
              {services.length} turnos
            </span>
          </div>

          <div className="flex flex-1 flex-col gap-3">
            {services.map((service) => (
              <div
                key={service.time}
                className="flex gap-3 rounded-xl border border-[#eff2f6] bg-[#fbfcfd] p-3 transition hover:border-[#d0dbe9]"
              >
                <div className="w-12 pt-0.5 text-xs font-bold text-[#172b4d]">
                  {service.time}
                </div>
                <div className="min-w-0 flex-1 border-l border-[#e6ebf2] pl-3">
                  <p className="truncate text-xs font-semibold text-[#172b4d]">
                    {service.client}
                  </p>
                  <p className="mt-1 flex items-center gap-1 truncate text-[11px] text-[#8a98aa]">
                    <MapPin size={11} className="shrink-0" />
                    <span>
                      {service.from} → {service.to}
                    </span>
                  </p>
                  <div className="mt-2 flex items-center justify-between text-[10px] text-[#5c6d83]">
                    <span className="inline-flex items-center gap-1">
                      <UserRound size={11} className="text-[#9aa7b7]" />
                      {service.driver}
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <Truck size={11} className="text-[#9aa7b7]" />
                      {service.vehicle}
                    </span>
                  </div>
                </div>
                <span
                  className={`mt-1 size-2 shrink-0 rounded-full ${service.color}`}
                  title={service.status}
                />
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={() => setModalNuevoTurno(true)}
            className="w-full rounded-xl border border-[#dfe6ef] py-2.5 text-xs font-bold text-[#2165d5] transition hover:bg-[#edf4ff]"
          >
            Agendar turno para este día
          </button>
        </aside>
      </div>

      {/* Modal interactivo de agendamiento rápido */}
      {modalNuevoTurno && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-[#172b4d]/40 p-4 backdrop-blur-xs">
          <div
            role="dialog"
            aria-modal="true"
            className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl"
          >
            <div className="flex items-start justify-between border-b border-[#edf0f4] pb-4">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-[#2165d5]">
                  Agenda operativa
                </p>
                <h3 className="mt-1 text-lg font-bold text-[#172b4d]">
                  Agendar nuevo turno
                </h3>
                <p className="mt-0.5 text-xs text-[#8b99ab]">
                  Para el {selectedDay} de {monthNames[month - 1]} de 2026.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setModalNuevoTurno(false)}
                className="rounded-lg p-1.5 text-[#8b99ab] hover:bg-[#f3f5f8]"
              >
                ✕
              </button>
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                setModalNuevoTurno(false);
              }}
              className="mt-5 flex flex-col gap-4"
            >
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="text-xs font-semibold text-[#62738a]">
                  Horario
                  <input
                    type="time"
                    defaultValue="09:00"
                    required
                    className="mt-1.5 w-full rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5]"
                  />
                </label>
                <label className="text-xs font-semibold text-[#62738a]">
                  Cliente
                  <input
                    placeholder="Nombre o empresa"
                    required
                    className="mt-1.5 w-full rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5]"
                  />
                </label>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <label className="text-xs font-semibold text-[#62738a]">
                  Origen
                  <input
                    placeholder="Ej. Palermo"
                    required
                    className="mt-1.5 w-full rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5]"
                  />
                </label>
                <label className="text-xs font-semibold text-[#62738a]">
                  Destino
                  <input
                    placeholder="Ej. Nordelta"
                    required
                    className="mt-1.5 w-full rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5]"
                  />
                </label>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <label className="text-xs font-semibold text-[#62738a]">
                  Chofer asignado
                  <select className="mt-1.5 w-full rounded-lg border border-[#dfe6ef] bg-white px-3 py-2 text-xs outline-none focus:border-[#2165d5]">
                    <option>Lucas Ramírez · Disponible</option>
                    <option>Sofía Martínez · Disponible</option>
                    <option>Diego Acosta · Disponible</option>
                    <option>Martín Soto · Disponible</option>
                  </select>
                </label>
                <label className="text-xs font-semibold text-[#62738a]">
                  Vehículo
                  <select className="mt-1.5 w-full rounded-lg border border-[#dfe6ef] bg-white px-3 py-2 text-xs outline-none focus:border-[#2165d5]">
                    <option>Camión chico (hasta 12 m³)</option>
                    <option>Camión grande (hasta 30 m³)</option>
                  </select>
                </label>
              </div>

              <div className="mt-2 flex justify-end gap-2 border-t border-[#edf0f4] pt-4">
                <button
                  type="button"
                  onClick={() => setModalNuevoTurno(false)}
                  className="rounded-lg border border-[#dfe6ef] px-4 py-2 text-xs font-semibold text-[#62738a] hover:bg-[#f7f9fc]"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-[#2165d5] px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-[#1857bd]"
                >
                  Confirmar turno
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
