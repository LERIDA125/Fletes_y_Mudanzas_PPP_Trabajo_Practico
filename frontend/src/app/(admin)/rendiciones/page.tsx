"use client";

import { ArrowDownToLine, Plus, Search, X } from "lucide-react";
import { useState } from "react";

type Rendicion = {
  id: string;
  chofer: string;
  servicio: string;
  fecha: string;
  tarifa: string;
  adelanto: string;
  gastos: string;
  saldo: string;
  estado: "Pendiente" | "Aprobada" | "En revisión";
  badgeColor: string;
};

const rows: Rendicion[] = [
  {
    id: "#REN-024",
    chofer: "Carlos Méndez",
    servicio: "María González (Palermo → Nordelta)",
    fecha: "23 sep · 08:30",
    tarifa: "$18.500",
    adelanto: "$12.000",
    gastos: "$2.500 (Peajes y combustible)",
    saldo: "$4.000",
    estado: "Pendiente",
    badgeColor: "bg-[#fff4e5] text-[#b86a16] dark:bg-[#3d2914] dark:text-[#fbbf24]",
  },
  {
    id: "#REN-023",
    chofer: "Lucía Fernández",
    servicio: "Estudio Norte (Belgrano → San Isidro)",
    fecha: "22 sep · 10:00",
    tarifa: "$16.000",
    adelanto: "$16.000",
    gastos: "$0",
    saldo: "$0",
    estado: "Aprobada",
    badgeColor: "bg-[#e9f8ef] text-[#248952] dark:bg-[#163827] dark:text-[#4ade80]",
  },
  {
    id: "#REN-022",
    chofer: "Diego Soto",
    servicio: "Tomás Rivas (Villa Urquiza → Colegiales)",
    fecha: "22 sep · 14:00",
    tarifa: "$15.500",
    adelanto: "$10.000",
    gastos: "$1.800 (Estacionamiento)",
    saldo: "$3.700",
    estado: "En revisión",
    badgeColor: "bg-[#e9f4ff] text-[#2879bd] dark:bg-[#1a3356] dark:text-[#60a5fa]",
  },
  {
    id: "#REN-021",
    chofer: "Sofía Acosta",
    servicio: "Ana López (Caballito → Vicente López)",
    fecha: "21 sep · 09:00",
    tarifa: "$17.000",
    adelanto: "$17.000",
    gastos: "$0",
    saldo: "$0",
    estado: "Aprobada",
    badgeColor: "bg-[#e9f8ef] text-[#248952] dark:bg-[#163827] dark:text-[#4ade80]",
  },
  {
    id: "#REN-020",
    chofer: "Lucas Ramírez",
    servicio: "Valentina Ruiz (Caballito → Haedo)",
    fecha: "20 sep · 16:30",
    tarifa: "$19.000",
    adelanto: "$15.000",
    gastos: "$1.500 (Peajes)",
    saldo: "$2.500",
    estado: "Aprobada",
    badgeColor: "bg-[#e9f8ef] text-[#248952] dark:bg-[#163827] dark:text-[#4ade80]",
  },
];

export default function PaginaRendiciones() {
  const [selectedRendicion, setSelectedRendicion] = useState<Rendicion | null>(null);
  const [modalNuevaRendicion, setModalNuevaRendicion] = useState(false);
  const [busqueda, setBusqueda] = useState("");

  const rendicionesFiltradas = rows.filter(
    (r) =>
      r.chofer.toLowerCase().includes(busqueda.toLowerCase()) ||
      r.id.toLowerCase().includes(busqueda.toLowerCase()) ||
      r.servicio.toLowerCase().includes(busqueda.toLowerCase()),
  );

  return (
    <div className="flex flex-col gap-6">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
            Control financiero
          </p>
          <h2 className="text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            Rendiciones
          </h2>
          <p className="mt-1 text-xs text-[#7f8da1] dark:text-[#94a3b8]">
            Revisá gastos, adelantos y cierres de cada servicio.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className="flex items-center gap-1.5 rounded-xl border border-[#dfe6ef] bg-white px-3.5 py-2.5 text-xs font-semibold text-[#62738a] shadow-xs hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:bg-[#111c2e] dark:text-[#cbd5e1] dark:hover:bg-[#16253d]"
          >
            <ArrowDownToLine size={15} />
            <span>Exportar CSV</span>
          </button>
          <button
            type="button"
            onClick={() => setModalNuevaRendicion(true)}
            className="flex items-center gap-2 rounded-xl bg-[#2165d5] px-4 py-2.5 text-xs font-bold text-white shadow-[0_5px_12px_rgba(33,101,213,0.18)] transition hover:bg-[#1857bd] dark:bg-[#2563eb] dark:hover:bg-[#1d4ed8]"
          >
            <Plus size={16} />
            <span>Nueva rendición</span>
          </button>
        </div>
      </div>

      {/* Tarjetas KPI Financieras */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
          <p className="text-xs font-medium text-[#8b99ab] dark:text-[#94a3b8]">
            Pendiente de rendición
          </p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            $50.000
          </p>
          <p className="mt-1 text-xs font-medium text-[#b86a16] dark:text-[#fbbf24]">
            2 servicios por cerrar
          </p>
        </div>

        <div className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
          <p className="text-xs font-medium text-[#8b99ab] dark:text-[#94a3b8]">
            Aprobado este mes
          </p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            $186.500
          </p>
          <p className="mt-1 text-xs font-medium text-[#248952] dark:text-[#4ade80]">
            +12,4% vs. agosto
          </p>
        </div>

        <div className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
          <p className="text-xs font-medium text-[#8b99ab] dark:text-[#94a3b8]">
            Tiempo promedio
          </p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-[#172b4d] sm:text-3xl dark:text-white">
            1,8 días
          </p>
          <p className="mt-1 text-xs font-medium text-[#2165d5] dark:text-[#60a5fa]">
            Dentro del objetivo operativo
          </p>
        </div>
      </div>

      {/* Tabla de rendiciones */}
      <section className="rounded-2xl border border-[#e8edf4] bg-white p-5 shadow-sm sm:p-6 dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-[#edf0f4] pb-4 dark:border-[#1e2c44]">
          <div>
            <h3 className="text-base font-bold text-[#172b4d] dark:text-white">
              Rendiciones de choferes
            </h3>
            <p className="mt-0.5 text-xs text-[#96a2b2] dark:text-[#94a3b8]">
              Controlá adelantos, gastos informados y saldos a pagar.
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-xl border border-[#dfe6ef] bg-[#fbfcfd] px-3 py-1.5 dark:border-[#1e2c44] dark:bg-[#0d1626]">
            <Search size={14} className="text-[#99a7b8] dark:text-[#64748b]" />
            <input
              type="text"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar por chofer o código..."
              className="w-48 bg-transparent text-xs text-[#172b4d] outline-none placeholder:text-[#aab4c1] dark:text-white dark:placeholder:text-[#64748b]"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[780px] text-left text-xs">
            <thead>
              <tr className="border-b border-[#f0f2f5] text-[10px] font-bold uppercase tracking-wider text-[#a0adbd] dark:border-[#1e2c44] dark:text-[#64748b]">
                <th className="px-3.5 py-3">Rendición</th>
                <th className="px-3.5 py-3">Chofer</th>
                <th className="px-3.5 py-3">Servicio</th>
                <th className="px-3.5 py-3">Fecha</th>
                <th className="px-3.5 py-3">Tarifa</th>
                <th className="px-3.5 py-3">Adelanto</th>
                <th className="px-3.5 py-3">Estado</th>
                <th className="px-3.5 py-3 text-right">Acción</th>
              </tr>
            </thead>
            <tbody>
              {rendicionesFiltradas.map((r) => (
                <tr
                  key={r.id}
                  className="border-b border-[#f1f3f6] text-xs transition hover:bg-[#fafcff] last:border-0 dark:border-[#1e2c44] dark:hover:bg-[#16253d]"
                >
                  <td className="px-3.5 py-4 font-bold text-[#2165d5] dark:text-[#60a5fa]">
                    {r.id}
                  </td>
                  <td className="px-3.5 py-4 font-semibold text-[#172b4d] dark:text-white">
                    {r.chofer}
                  </td>
                  <td className="max-w-[220px] truncate px-3.5 py-4 text-[#718096] dark:text-[#94a3b8]">
                    {r.servicio}
                  </td>
                  <td className="px-3.5 py-4 text-[#718096] dark:text-[#94a3b8]">
                    {r.fecha}
                  </td>
                  <td className="px-3.5 py-4 font-semibold text-[#172b4d] dark:text-white">
                    {r.tarifa}
                  </td>
                  <td className="px-3.5 py-4 text-[#718096] dark:text-[#94a3b8]">
                    {r.adelanto}
                  </td>
                  <td className="px-3.5 py-4">
                    <span
                      className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold ${r.badgeColor}`}
                    >
                      {r.estado}
                    </span>
                  </td>
                  <td className="px-3.5 py-4 text-right">
                    <button
                      type="button"
                      onClick={() => setSelectedRendicion(r)}
                      className="font-bold text-[#2165d5] hover:underline dark:text-[#60a5fa]"
                    >
                      Ver detalle
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Modal detalle de rendición */}
      {selectedRendicion && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-[#172b4d]/40 p-4 backdrop-blur-xs">
          <div
            role="dialog"
            aria-modal="true"
            className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl dark:border dark:border-[#1e2c44] dark:bg-[#111c2e]"
          >
            <div className="flex items-start justify-between border-b border-[#edf0f4] pb-4 dark:border-[#1e2c44]">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
                  Liquidación de viaje
                </p>
                <h3 className="mt-1 text-lg font-bold text-[#172b4d] dark:text-white">
                  Detalle de rendición {selectedRendicion.id}
                </h3>
                <p className="mt-0.5 text-xs text-[#8b99ab] dark:text-[#94a3b8]">
                  {selectedRendicion.chofer} · {selectedRendicion.fecha}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedRendicion(null)}
                className="rounded-lg p-1.5 text-[#8b99ab] hover:bg-[#f3f5f8] dark:hover:bg-[#18263d]"
              >
                <X size={18} />
              </button>
            </div>

            <div className="mt-5 flex flex-col gap-4 text-xs">
              <div className="rounded-xl border border-[#e8edf4] bg-[#f8fbff] p-4 dark:border-[#1e2c44] dark:bg-[#0d1626]">
                <p className="font-semibold text-[#172b4d] dark:text-white">
                  {selectedRendicion.servicio}
                </p>
                <div className="mt-3 grid grid-cols-2 gap-3 border-t border-[#e8edf4] pt-3 dark:border-[#1e2c44]">
                  <div>
                    <span className="text-[#8b99ab] dark:text-[#64748b]">
                      Tarifa acordada:
                    </span>
                    <p className="text-sm font-bold text-[#172b4d] dark:text-white">
                      {selectedRendicion.tarifa}
                    </p>
                  </div>
                  <div>
                    <span className="text-[#8b99ab] dark:text-[#64748b]">
                      Adelanto entregado:
                    </span>
                    <p className="text-sm font-bold text-[#172b4d] dark:text-white">
                      {selectedRendicion.adelanto}
                    </p>
                  </div>
                </div>
              </div>

              <div className="rounded-xl border border-[#edf0f4] p-4 dark:border-[#1e2c44] dark:bg-[#0d1626]">
                <p className="font-semibold text-[#172b4d] dark:text-white">
                  Gastos informados:
                </p>
                <p className="mt-1 text-[#62738a] dark:text-[#94a3b8]">
                  {selectedRendicion.gastos}
                </p>
                <div className="mt-3 flex items-center justify-between border-t border-[#edf0f4] pt-3 font-semibold dark:border-[#1e2c44]">
                  <span className="text-[#172b4d] dark:text-white">
                    Saldo a liquidar al chofer:
                  </span>
                  <span className="text-sm font-bold text-[#2165d5] dark:text-[#60a5fa]">
                    {selectedRendicion.saldo}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2 border-t border-[#edf0f4] pt-4 dark:border-[#1e2c44]">
              <button
                type="button"
                onClick={() => setSelectedRendicion(null)}
                className="rounded-lg border border-[#dfe6ef] px-4 py-2 text-xs font-semibold text-[#62738a] hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:text-[#94a3b8] dark:hover:bg-[#16253d]"
              >
                Cerrar
              </button>
              {selectedRendicion.estado !== "Aprobada" && (
                <button
                  type="button"
                  onClick={() => setSelectedRendicion(null)}
                  className="rounded-lg bg-[#248952] px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-[#1e7244]"
                >
                  Aprobar rendición
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal nueva rendición */}
      {modalNuevaRendicion && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-[#172b4d]/40 p-4 backdrop-blur-xs">
          <div
            role="dialog"
            aria-modal="true"
            className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl dark:border dark:border-[#1e2c44] dark:bg-[#111c2e]"
          >
            <div className="flex items-start justify-between border-b border-[#edf0f4] pb-4 dark:border-[#1e2c44]">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-[#2165d5] dark:text-[#60a5fa]">
                  Arqueo de caja
                </p>
                <h3 className="mt-1 text-lg font-bold text-[#172b4d] dark:text-white">
                  Registrar nueva rendición
                </h3>
                <p className="mt-0.5 text-xs text-[#8b99ab] dark:text-[#94a3b8]">
                  Ingresá la liquidación entregada por el chofer al finalizar el servicio.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setModalNuevaRendicion(false)}
                className="rounded-lg p-1.5 text-[#8b99ab] hover:bg-[#f3f5f8] dark:hover:bg-[#18263d]"
              >
                <X size={18} />
              </button>
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                setModalNuevaRendicion(false);
              }}
              className="mt-5 flex flex-col gap-4 text-xs"
            >
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="font-semibold text-[#62738a] dark:text-[#94a3b8]">
                  Chofer
                  <select className="mt-1.5 w-full rounded-lg border border-[#dfe6ef] bg-white px-3 py-2 text-xs outline-none focus:border-[#2165d5] dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white">
                    <option>Carlos Méndez</option>
                    <option>Lucía Fernández</option>
                    <option>Diego Soto</option>
                    <option>Sofía Acosta</option>
                  </select>
                </label>
                <label className="font-semibold text-[#62738a] dark:text-[#94a3b8]">
                  Servicio asignado
                  <select className="mt-1.5 w-full rounded-lg border border-[#dfe6ef] bg-white px-3 py-2 text-xs outline-none focus:border-[#2165d5] dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white">
                    <option>SRV-101 · María González</option>
                    <option>SRV-102 · Estudio Norte</option>
                    <option>SRV-103 · Tomás Rivas</option>
                  </select>
                </label>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <label className="font-semibold text-[#62738a] dark:text-[#94a3b8]">
                  Monto recaudado en efectivo
                  <input
                    type="text"
                    defaultValue="$ 18.500"
                    className="mt-1.5 w-full rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5] dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white"
                  />
                </label>
                <label className="font-semibold text-[#62738a] dark:text-[#94a3b8]">
                  Adelanto previo
                  <input
                    type="text"
                    defaultValue="$ 12.000"
                    className="mt-1.5 w-full rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5] dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white"
                  />
                </label>
              </div>

              <label className="font-semibold text-[#62738a] dark:text-[#94a3b8]">
                Gastos informados (peajes, combustible, otros)
                <textarea
                  rows={2}
                  placeholder="Detallar comprobantes y gastos..."
                  className="mt-1.5 w-full resize-none rounded-lg border border-[#dfe6ef] px-3 py-2 text-xs outline-none focus:border-[#2165d5] dark:border-[#1e2c44] dark:bg-[#0d1626] dark:text-white"
                />
              </label>

              <div className="flex justify-end gap-2 border-t border-[#edf0f4] pt-4 dark:border-[#1e2c44]">
                <button
                  type="button"
                  onClick={() => setModalNuevaRendicion(false)}
                  className="rounded-lg border border-[#dfe6ef] px-4 py-2 text-xs font-semibold text-[#62738a] hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:text-[#94a3b8] dark:hover:bg-[#16253d]"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-[#2165d5] px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-[#1857bd] dark:bg-[#2563eb] dark:hover:bg-[#1d4ed8]"
                >
                  Guardar rendición
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
