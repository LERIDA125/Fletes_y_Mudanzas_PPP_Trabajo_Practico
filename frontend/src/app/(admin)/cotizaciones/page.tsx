"use client";

import { CheckCircle2, CircleDollarSign, Send } from "lucide-react";
import { useState } from "react";

export default function PaginaCotizaciones() {
  const [vehicle, setVehicle] = useState("Camión grande");
  const [distance, setDistance] = useState("18");
  const [stairs, setStairs] = useState(false);
  const [packing, setPacking] = useState(false);
  const [sentSuccess, setSentSuccess] = useState(false);

  const base = vehicle === "Camión grande" ? 24000 : 16000;
  const distanceCost = Math.max(0, Number(distance || 0) - 10) * 650;
  const stairsCost = stairs ? 4500 : 0;
  const packingCost = packing ? 8500 : 0;
  const total = base + distanceCost + stairsCost + packingCost;

  const money = new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    maximumFractionDigits: 0,
  });

  const recentQuotes = [
    {
      name: "María González",
      amount: "$28.500",
      status: "Enviada",
      badge: "bg-[#edf4ff] text-[#2165d5]",
    },
    {
      name: "Estudio Norte",
      amount: "$16.000",
      status: "Borrador",
      badge: "bg-[#fff4e5] text-[#b86a16]",
    },
    {
      name: "Tomás Rivas",
      amount: "$33.000",
      status: "Aceptada",
      badge: "bg-[#e9f8ef] text-[#248952]",
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5]">
            Calculadora comercial
          </p>
          <h2 className="text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl">
            Cotizaciones
          </h2>
          <p className="mt-1 text-xs text-[#7f8da1]">
            Armá presupuestos exactos y compartilos con tus clientes.
          </p>
        </div>
      </div>

      {/* Grid del Cotizador */}
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        {/* Formulario */}
        <section className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-3 border-b border-[#edf0f4] pb-5">
            <div>
              <h3 className="text-base font-bold text-[#172b4d]">Nueva cotización</h3>
              <p className="mt-0.5 text-xs text-[#96a2b2]">
                Calculá un presupuesto exacto para compartir con tu cliente.
              </p>
            </div>
            <span className="rounded-full bg-[#e9f8ef] px-3 py-1 text-xs font-semibold text-[#248952]">
              Borrador guardado
            </span>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <label className="flex flex-col gap-1.5 text-xs font-semibold text-[#62738a]">
              Cliente
              <input
                className="rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5]"
                placeholder="Nombre o razón social"
              />
            </label>
            <label className="flex flex-col gap-1.5 text-xs font-semibold text-[#62738a]">
              Teléfono
              <input
                className="rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5]"
                placeholder="+54 9 11..."
              />
            </label>
            <label className="flex flex-col gap-1.5 text-xs font-semibold text-[#62738a] sm:col-span-2">
              Origen y destino
              <input
                className="rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5]"
                placeholder="Ej. Palermo → Nordelta"
              />
            </label>
          </div>

          <div className="mt-6">
            <p className="text-xs font-bold text-[#62738a]">Datos del servicio</p>
            <div className="mt-3 grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-1.5 text-xs font-semibold text-[#62738a]">
                Tipo de camión
                <select
                  value={vehicle}
                  onChange={(e) => setVehicle(e.target.value)}
                  className="rounded-lg border border-[#dfe6ef] bg-white px-3 py-2 text-xs outline-none focus:border-[#2165d5]"
                >
                  <option>Camión chico</option>
                  <option>Camión grande</option>
                </select>
              </label>
              <label className="flex flex-col gap-1.5 text-xs font-semibold text-[#62738a]">
                Distancia estimada (km)
                <input
                  type="number"
                  min="0"
                  value={distance}
                  onChange={(e) => setDistance(e.target.value)}
                  className="rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5]"
                />
              </label>
            </div>

            <div className="mt-4 grid gap-2 sm:grid-cols-2">
              <label className="flex cursor-pointer items-center gap-3 rounded-xl border border-[#edf0f4] p-3 text-xs text-[#62738a] hover:bg-[#fafcff]">
                <input
                  type="checkbox"
                  checked={stairs}
                  onChange={(e) => setStairs(e.target.checked)}
                  className="accent-[#2165d5]"
                />
                <span>Acceso por escalera</span>
                <span className="ml-auto font-bold text-[#172b4d]">+ $4.500</span>
              </label>
              <label className="flex cursor-pointer items-center gap-3 rounded-xl border border-[#edf0f4] p-3 text-xs text-[#62738a] hover:bg-[#fafcff]">
                <input
                  type="checkbox"
                  checked={packing}
                  onChange={(e) => setPacking(e.target.checked)}
                  className="accent-[#2165d5]"
                />
                <span>Embalaje y protección</span>
                <span className="ml-auto font-bold text-[#172b4d]">+ $8.500</span>
              </label>
            </div>
          </div>

          <label className="mt-6 flex flex-col gap-1.5 text-xs font-semibold text-[#62738a]">
            Notas para el equipo operativo
            <textarea
              rows={3}
              className="resize-none rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5]"
              placeholder="Objetos delicados, restricciones de horario, observaciones..."
            />
          </label>
        </section>

        {/* Panel lateral: Total y desglose */}
        <aside className="flex flex-col gap-4">
          <section className="rounded-2xl bg-[#172b4d] p-5 text-white shadow-[0_8px_24px_rgba(23,43,77,0.12)]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-[#aebed4]">Total estimado</p>
                <p className="mt-2 text-3xl font-bold tracking-tight">
                  {money.format(total)}
                </p>
              </div>
              <div className="grid size-10 place-items-center rounded-xl bg-white/10">
                <CircleDollarSign size={20} />
              </div>
            </div>

            <div className="mt-5 flex flex-col gap-2 border-t border-white/10 pt-4 text-xs text-[#c5d1e1]">
              <div className="flex justify-between">
                <span>Base {vehicle.toLowerCase()}</span>
                <span className="font-semibold text-white">{money.format(base)}</span>
              </div>
              <div className="flex justify-between">
                <span>Distancia adicional</span>
                <span className="font-semibold text-white">
                  {money.format(distanceCost)}
                </span>
              </div>
              {stairs && (
                <div className="flex justify-between">
                  <span>Escaleras</span>
                  <span className="font-semibold text-white">
                    {money.format(stairsCost)}
                  </span>
                </div>
              )}
              {packing && (
                <div className="flex justify-between">
                  <span>Embalaje</span>
                  <span className="font-semibold text-white">
                    {money.format(packingCost)}
                  </span>
                </div>
              )}
            </div>
          </section>

          <button
            type="button"
            onClick={() => {
              setSentSuccess(true);
              setTimeout(() => setSentSuccess(false), 3000);
            }}
            className="flex items-center justify-center gap-2 rounded-xl bg-[#2165d5] px-4 py-3 text-xs font-bold text-white shadow-[0_5px_12px_rgba(33,101,213,0.18)] transition hover:bg-[#1857bd]"
          >
            {sentSuccess ? (
              <>
                <CheckCircle2 size={16} />
                <span>¡Cotización guardada!</span>
              </>
            ) : (
              <>
                <Send size={15} />
                <span>Guardar y enviar cotización</span>
              </>
            )}
          </button>

          {/* Cotizaciones recientes */}
          <section className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-[#172b4d]">Cotizaciones recientes</h4>
              <button
                type="button"
                className="text-xs font-bold text-[#2165d5] hover:underline"
              >
                Ver todas
              </button>
            </div>

            <div className="mt-4 flex flex-col gap-3">
              {recentQuotes.map((q) => (
                <div
                  key={q.name}
                  className="flex items-center justify-between border-b border-[#f0f2f5] pb-3 last:border-0 last:pb-0 text-xs"
                >
                  <div>
                    <p className="font-semibold text-[#172b4d]">{q.name}</p>
                    <span
                      className={`mt-1 inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold ${q.badge}`}
                    >
                      {q.status}
                    </span>
                  </div>
                  <p className="font-bold text-[#172b4d]">{q.amount}</p>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}
