"use client";

import { KeyRound, ShieldCheck, Smartphone, Truck } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import {
  guardarSesionCliente,
  iniciarSesionApi,
  limpiarSesionCliente,
  obtenerUsuarioSesionLocal,
} from "@/lib/api/auth";
import { ErrorApi } from "@/lib/api/http";

export default function PaginaLogin() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sesionActual = obtenerUsuarioSesionLocal();

  async function manejarSubmit(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setError(null);
    setCargando(true);
    try {
      const respuesta = await iniciarSesionApi({
        username: username.trim(),
        password,
      });
      guardarSesionCliente(respuesta);
      if (respuesta.usuario.rol === "chofer") {
        router.push("/chofer");
      } else {
        router.push("/");
      }
      router.refresh();
    } catch (err) {
      if (err instanceof ErrorApi) {
        setError(err.message);
      } else {
        setError("No se pudo iniciar sesión. Verificá tus credenciales.");
      }
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col justify-center bg-[#f7f9fc] px-4 py-12 dark:bg-[#0b1320]">
      <div className="mx-auto w-full max-w-md rounded-3xl border border-[#e6ebf2] bg-white p-8 shadow-sm dark:border-[#1e2c44] dark:bg-[#111c2e]">
        <div className="flex items-center gap-3">
          <div className="grid size-11 place-items-center rounded-2xl bg-[#2165d5] text-white shadow-xs">
            <Truck size={22} strokeWidth={2.4} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-[#172b4d] dark:text-white">
              Fletes y Mudanzas Express
            </h1>
            <p className="text-xs text-[#6b7a90] dark:text-[#94a3b8]">
              Acceso con JWT por rol (Administrador / Chofer)
            </p>
          </div>
        </div>

        {sesionActual && (
          <div className="mt-5 flex items-center justify-between rounded-2xl border border-[#dbe7ff] bg-[#f4f8ff] px-4 py-3 text-xs text-[#1e3a66] dark:border-[#243b61] dark:bg-[#16253d] dark:text-[#bfdbfe]">
            <span>
              Sesión activa: <strong>{sesionActual.username}</strong> ({sesionActual.rol})
            </span>
            <button
              type="button"
              onClick={() => {
                limpiarSesionCliente();
                router.refresh();
              }}
              className="font-bold text-[#2165d5] hover:underline dark:text-[#60a5fa]"
            >
              Cerrar sesión
            </button>
          </div>
        )}

        <form onSubmit={manejarSubmit} className="mt-6 space-y-4">
          <div>
            <label
              htmlFor="login-username"
              className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-[#5e6e85] dark:text-[#94a3b8]"
            >
              Usuario
            </label>
            <input
              id="login-username"
              type="text"
              required
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Ej. admin, socio o chofer1"
              className="w-full rounded-xl border border-[#dce3ee] bg-[#fafcff] px-3.5 py-2.5 text-sm text-[#172b4d] outline-none focus:border-[#2165d5] dark:border-[#243552] dark:bg-[#0f172a] dark:text-white"
            />
          </div>

          <div>
            <label
              htmlFor="login-password"
              className="mb-1.5 block text-xs font-bold uppercase tracking-wider text-[#5e6e85] dark:text-[#94a3b8]"
            >
              Contraseña
            </label>
            <input
              id="login-password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full rounded-xl border border-[#dce3ee] bg-[#fafcff] px-3.5 py-2.5 text-sm text-[#172b4d] outline-none focus:border-[#2165d5] dark:border-[#243552] dark:bg-[#0f172a] dark:text-white"
            />
          </div>

          {error && (
            <div
              role="alert"
              className="rounded-xl border border-rose-200 bg-rose-50 px-3.5 py-2.5 text-xs font-semibold text-rose-700 dark:border-rose-900/60 dark:bg-rose-950/50 dark:text-rose-300"
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={cargando}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#2165d5] px-4 py-3 text-sm font-bold text-white shadow-xs transition hover:bg-[#1954b8] disabled:opacity-60"
          >
            <KeyRound size={16} />
            <span>{cargando ? "Verificando token..." : "Iniciar sesión"}</span>
          </button>
        </form>

        <div className="mt-6 space-y-2 border-t border-[#eef1f6] pt-4 text-xs text-[#6b7a90] dark:border-[#1e2c44] dark:text-[#94a3b8]">
          <p className="font-semibold text-[#172b4d] dark:text-white">
            Accesos rápidos del entorno de demostración:
          </p>
          <div className="grid grid-cols-2 gap-2 pt-1">
            <Link
              href="/usuarios"
              className="flex items-center gap-1.5 rounded-xl border border-[#e3e9f2] px-3 py-2 font-semibold text-[#172b4d] hover:bg-[#f4f8ff] dark:border-[#243552] dark:text-slate-200 dark:hover:bg-[#16253d]"
            >
              <ShieldCheck size={14} className="text-[#2165d5]" />
              <span>Panel Multi-Admin</span>
            </Link>
            <Link
              href="/chofer"
              className="flex items-center gap-1.5 rounded-xl border border-[#e3e9f2] px-3 py-2 font-semibold text-[#172b4d] hover:bg-[#f4f8ff] dark:border-[#243552] dark:text-slate-200 dark:hover:bg-[#16253d]"
            >
              <Smartphone size={14} className="text-[#2165d5]" />
              <span>Portal del Chofer</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
