"use client";

import { ShieldCheck, Truck, UserCheck, UserPlus } from "lucide-react";
import { useState, type FormEvent } from "react";

import type { Chofer } from "@/features/choferes/types";
import type { Servicio } from "@/features/servicios/types";
import { crearUsuarioApi, type UsuarioRead } from "@/lib/api/auth";
import { ErrorApi } from "@/lib/api/http";

type Props = {
  usuariosIniciales: UsuarioRead[];
  choferesActivos: Chofer[];
  serviciosRecientes: Servicio[];
};

export function PanelUsuarios({
  usuariosIniciales,
  choferesActivos,
  serviciosRecientes,
}: Props) {
  const [usuarios, setUsuarios] = useState<UsuarioRead[]>(usuariosIniciales);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [rol, setRol] = useState<"admin" | "chofer">("chofer");
  const [idChofer, setIdChofer] = useState<string>("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mensajeExito, setMensajeExito] = useState<string | null>(null);

  const choferesConCuenta = new Set(
    usuarios.map((u) => u.id_chofer).filter((id): id is number => typeof id === "number"),
  );
  const choferesDisponibles = choferesActivos.filter((c) => !choferesConCuenta.has(c.id));

  const mapaUsuarios = new Map<number, string>(
    usuarios.map((u) => [u.id, `${u.username} (${u.rol})`]),
  );
  const mapaChoferes = new Map<number, string>(
    choferesActivos.map((c) => [c.id, c.nombre_completo]),
  );

  function describirAutor(idAutor: number | null | undefined): string {
    if (!idAutor) {
      return "Admin (modo dev)";
    }
    return mapaUsuarios.get(idAutor) ?? `Usuario #${idAutor}`;
  }

  async function manejarAltaUsuario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setError(null);
    setMensajeExito(null);

    if (rol === "chofer" && !idChofer) {
      setError("Seleccioná el chofer de la flota al que pertenece este usuario.");
      return;
    }

    setEnviando(true);
    try {
      const creado = await crearUsuarioApi({
        username: username.trim(),
        password,
        rol,
        id_chofer: rol === "chofer" ? Number(idChofer) : null,
      });
      setUsuarios((prev) => [...prev, creado]);
      setUsername("");
      setPassword("");
      setIdChofer("");
      setMensajeExito(
        rol === "admin"
          ? `Se creó la cuenta de administrador "${creado.username}".`
          : `Se creó el acceso móvil "${creado.username}" para el chofer seleccionado.`,
      );
    } catch (err) {
      if (err instanceof ErrorApi) {
        setError(err.message);
      } else {
        setError("No se pudo registrar el usuario.");
      }
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="space-y-7">
      <div className="grid gap-6 lg:grid-cols-12">
        {/* Formulario de alta Multi-Admin / Usuario Chofer */}
        <section className="rounded-3xl border border-[#e6ebf2] bg-white p-6 shadow-xs lg:col-span-5 dark:border-[#1e2c44] dark:bg-[#111c2e]">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-2xl bg-[#edf4ff] text-[#2165d5] dark:bg-[#1e3458] dark:text-[#60a5fa]">
              <UserPlus size={19} />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#172b4d] dark:text-white">
                Crear cuenta de acceso
              </h2>
              <p className="text-xs text-[#718096] dark:text-[#94a3b8]">
                Habilitá un nuevo socio administrador o creale el usuario a un chofer.
              </p>
            </div>
          </div>

          <form onSubmit={manejarAltaUsuario} className="mt-5 space-y-4">
            <div>
              <label
                htmlFor="rol-usuario"
                className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-[#5e6e85] dark:text-[#94a3b8]"
              >
                Rol en el sistema
              </label>
              <select
                id="rol-usuario"
                value={rol}
                onChange={(e) => setRol(e.target.value as "admin" | "chofer")}
                className="w-full rounded-xl border border-[#dce3ee] bg-[#fafcff] px-3.5 py-2.5 text-sm font-medium text-[#172b4d] outline-none focus:border-[#2165d5] dark:border-[#243552] dark:bg-[#0f172a] dark:text-white"
              >
                <option value="chofer">Chofer (acceso restringido a sus viajes)</option>
                <option value="admin">Administrador / Dueño (acceso total)</option>
              </select>
            </div>

            {rol === "chofer" && (
              <div>
                <label
                  htmlFor="select-chofer"
                  className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-[#5e6e85] dark:text-[#94a3b8]"
                >
                  Chofer vinculado
                </label>
                <select
                  id="select-chofer"
                  value={idChofer}
                  onChange={(e) => setIdChofer(e.target.value)}
                  className="w-full rounded-xl border border-[#dce3ee] bg-[#fafcff] px-3.5 py-2.5 text-sm text-[#172b4d] outline-none focus:border-[#2165d5] dark:border-[#243552] dark:bg-[#0f172a] dark:text-white"
                >
                  <option value="">Seleccionar chofer activo...</option>
                  {choferesDisponibles.map((chofer) => (
                    <option key={chofer.id} value={chofer.id}>
                      {chofer.nombre_completo} (ID #{chofer.id})
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div>
              <label
                htmlFor="nuevo-username"
                className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-[#5e6e85] dark:text-[#94a3b8]"
              >
                Nombre de usuario
              </label>
              <input
                id="nuevo-username"
                type="text"
                required
                minLength={3}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={rol === "admin" ? "ej. socio.martinez" : "ej. chofer.carlos"}
                className="w-full rounded-xl border border-[#dce3ee] bg-[#fafcff] px-3.5 py-2.5 text-sm text-[#172b4d] outline-none focus:border-[#2165d5] dark:border-[#243552] dark:bg-[#0f172a] dark:text-white"
              />
            </div>

            <div>
              <label
                htmlFor="nuevo-password"
                className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-[#5e6e85] dark:text-[#94a3b8]"
              >
                Contraseña inicial
              </label>
              <input
                id="nuevo-password"
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Mínimo 6 caracteres"
                className="w-full rounded-xl border border-[#dce3ee] bg-[#fafcff] px-3.5 py-2.5 text-sm text-[#172b4d] outline-none focus:border-[#2165d5] dark:border-[#243552] dark:bg-[#0f172a] dark:text-white"
              />
            </div>

            {error && (
              <p
                role="alert"
                className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700 dark:border-rose-900/50 dark:bg-rose-950/40 dark:text-rose-300"
              >
                {error}
              </p>
            )}

            {mensajeExito && (
              <p
                role="status"
                className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700 dark:border-emerald-900/50 dark:bg-emerald-950/40 dark:text-emerald-300"
              >
                {mensajeExito}
              </p>
            )}

            <button
              type="submit"
              disabled={enviando}
              className="w-full rounded-xl bg-[#2165d5] px-4 py-2.5 text-sm font-bold text-white shadow-xs transition hover:bg-[#1954b8] disabled:opacity-60"
            >
              {enviando ? "Creando cuenta..." : "Registrar usuario"}
            </button>
          </form>
        </section>

        {/* Listado de cuentas Multi-Admin y Choferes */}
        <section className="rounded-3xl border border-[#e6ebf2] bg-white p-6 shadow-xs lg:col-span-7 dark:border-[#1e2c44] dark:bg-[#111c2e]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="grid size-10 place-items-center rounded-2xl bg-[#edf4ff] text-[#2165d5] dark:bg-[#1e3458] dark:text-[#60a5fa]">
                <ShieldCheck size={19} />
              </div>
              <div>
                <h2 className="text-base font-bold text-[#172b4d] dark:text-white">
                  Usuarios y Administradores ({usuarios.length})
                </h2>
                <p className="text-xs text-[#718096] dark:text-[#94a3b8]">
                  Cuentas habilitadas con trazabilidad de quién dio de alta cada acceso.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-5 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#eef1f6] text-[11px] font-bold uppercase tracking-wider text-[#8d9bb0] dark:border-[#1e2c44]">
                  <th className="pb-3 pr-3">Usuario</th>
                  <th className="pb-3 px-3">Rol</th>
                  <th className="pb-3 px-3">Chofer vinculado</th>
                  <th className="pb-3 pl-3">Creado por</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f1f4f9] dark:divide-[#1e2c44]">
                {usuarios.length === 0 ? (
                  <tr>
                    <td
                      colSpan={4}
                      className="py-6 text-center text-xs text-[#718096] dark:text-[#94a3b8]"
                    >
                      Todavía no hay usuarios registrados en la tabla usuarios.
                    </td>
                  </tr>
                ) : (
                  usuarios.map((u) => (
                    <tr key={u.id}>
                      <td className="py-3 pr-3 font-bold text-[#172b4d] dark:text-white">
                        {u.username}
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-bold ${
                            u.rol === "admin"
                              ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300"
                              : "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300"
                          }`}
                        >
                          {u.rol === "admin" ? (
                            <ShieldCheck size={12} />
                          ) : (
                            <Truck size={12} />
                          )}
                          {u.rol === "admin" ? "Administrador" : "Chofer"}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-[#4a5b73] dark:text-[#cbd5e1]">
                        {u.id_chofer
                          ? `${mapaChoferes.get(u.id_chofer) ?? "Chofer"} (#${u.id_chofer})`
                          : "—"}
                      </td>
                      <td className="py-3 pl-3 text-[#6b7a90] dark:text-[#94a3b8]">
                        {describirAutor(u.creado_por_id)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      {/* Auditoría de operaciones críticas (Quién creó y quién modificó) */}
      <section className="rounded-3xl border border-[#e6ebf2] bg-white p-6 shadow-xs dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <div className="flex items-center gap-3">
          <div className="grid size-10 place-items-center rounded-2xl bg-[#edf4ff] text-[#2165d5] dark:bg-[#1e3458] dark:text-[#60a5fa]">
            <UserCheck size={19} />
          </div>
          <div>
            <h2 className="text-base font-bold text-[#172b4d] dark:text-white">
              Trazabilidad y Auditoría de Operaciones (&ldquo;Quién hizo qué&rdquo;)
            </h2>
            <p className="text-xs text-[#718096] dark:text-[#94a3b8]">
              Registro automático de creado_por_id y modificado_por_id extraído del token
              JWT en cada servicio.
            </p>
          </div>
        </div>

        <div className="mt-5 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#eef1f6] text-[11px] font-bold uppercase tracking-wider text-[#8d9bb0] dark:border-[#1e2c44]">
                <th className="pb-3 pr-3">Servicio</th>
                <th className="pb-3 px-3">Cliente</th>
                <th className="pb-3 px-3">Chofer asignado</th>
                <th className="pb-3 px-3">Estado actual</th>
                <th className="pb-3 px-3">Creado por</th>
                <th className="pb-3 pl-3">Última modificación por</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#f1f4f9] dark:divide-[#1e2c44]">
              {serviciosRecientes.slice(0, 10).map((s) => (
                <tr key={s.id_servicio}>
                  <td className="py-3 pr-3 font-bold text-[#172b4d] dark:text-white">
                    #{s.id_servicio} ({s.fecha})
                  </td>
                  <td className="py-3 px-3 text-[#4a5b73] dark:text-[#cbd5e1]">
                    {s.razon_social_cliente}
                  </td>
                  <td className="py-3 px-3 text-[#4a5b73] dark:text-[#cbd5e1]">
                    {s.nombre_chofer ?? "Sin asignar"}
                  </td>
                  <td className="py-3 px-3 font-semibold text-[#2165d5] dark:text-[#60a5fa]">
                    {s.estado}
                  </td>
                  <td className="py-3 px-3 text-[#6b7a90] dark:text-[#94a3b8]">
                    {describirAutor(s.creado_por_id)}
                  </td>
                  <td className="py-3 pl-3 text-[#6b7a90] dark:text-[#94a3b8]">
                    {describirAutor(s.modificado_por_id)}
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
