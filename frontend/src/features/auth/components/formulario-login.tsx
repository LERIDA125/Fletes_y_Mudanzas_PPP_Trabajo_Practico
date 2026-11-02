"use client";

import {
  ArrowRight,
  KeyRound,
  Loader2,
  LockKeyhole,
  ShieldCheck,
  Truck,
  UserRound,
} from "lucide-react";
import { useActionState, useState } from "react";

import { iniciarSesion, type EstadoLogin } from "@/features/auth/actions";

const ESTADO_INICIAL: EstadoLogin = {};

export function FormularioLogin() {
  const [estado, accion, pendiente] = useActionState(iniciarSesion, ESTADO_INICIAL);
  const [usuario, setUsuario] = useState("");
  const [password, setPassword] = useState("");

  function llenarCredenciales(u: string, p: string) {
    setUsuario(u);
    setPassword(p);
  }

  return (
    <form action={accion} className="flex flex-col gap-5" noValidate>
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="username"
          className="text-xs font-semibold uppercase tracking-wider text-[#5f7087] dark:text-[#94a3b8]"
        >
          Usuario
        </label>
        <div className="relative">
          <UserRound
            aria-hidden="true"
            size={17}
            className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-[#8b99ab] dark:text-[#64748b]"
          />
          <input
            id="username"
            name="username"
            type="text"
            value={usuario}
            onChange={(e) => setUsuario(e.target.value)}
            autoComplete="username"
            autoCapitalize="none"
            spellCheck={false}
            required
            aria-invalid={Boolean(estado.error)}
            className="block min-h-11 w-full rounded-xl border border-[#dfe6ef] bg-white py-2.5 pr-3 pl-10 text-sm text-[#172b4d] shadow-xs transition-colors placeholder:text-[#a5b1c2] focus:border-[#2165d5] focus:ring-4 focus:ring-[#2165d5]/15 focus:outline-none dark:border-[#243651] dark:bg-[#0d1626] dark:text-white dark:placeholder:text-[#475569]"
            placeholder="tu.usuario"
          />
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="password"
          className="text-xs font-semibold uppercase tracking-wider text-[#5f7087] dark:text-[#94a3b8]"
        >
          Contraseña
        </label>
        <div className="relative">
          <LockKeyhole
            aria-hidden="true"
            size={17}
            className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-[#8b99ab] dark:text-[#64748b]"
          />
          <input
            id="password"
            name="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
            aria-invalid={Boolean(estado.error)}
            className="block min-h-11 w-full rounded-xl border border-[#dfe6ef] bg-white py-2.5 pr-3 pl-10 text-sm text-[#172b4d] shadow-xs transition-colors placeholder:text-[#a5b1c2] focus:border-[#2165d5] focus:ring-4 focus:ring-[#2165d5]/15 focus:outline-none dark:border-[#243651] dark:bg-[#0d1626] dark:text-white dark:placeholder:text-[#475569]"
            placeholder="••••••••••••"
          />
        </div>
      </div>

      {estado.error ? (
        <p
          role="alert"
          className="rounded-xl border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm font-medium text-red-700 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-300"
        >
          {estado.error}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={pendiente}
        className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-[#2165d5] px-4 text-sm font-bold text-white shadow-[0_8px_20px_rgba(33,101,213,0.24)] transition hover:bg-[#1857bd] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2165d5] disabled:cursor-not-allowed disabled:opacity-60 dark:bg-[#2563eb] dark:hover:bg-[#1d4ed8]"
      >
        {pendiente ? (
          <>
            <Loader2 aria-hidden="true" size={17} className="animate-spin" />
            Ingresando…
          </>
        ) : (
          <>
            Iniciar sesión
            <ArrowRight aria-hidden="true" size={17} />
          </>
        )}
      </button>

      {/* Accesos rápidos de desarrollo / demo para el equipo */}
      <div className="rounded-2xl border border-gray-200 bg-gray-50/70 p-3.5 dark:border-gray-800 dark:bg-gray-900/40">
        <p className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">
          <KeyRound size={13} className="text-[#2165d5]" />
          Accesos rápidos de prueba
        </p>
        <div className="mt-2.5 grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => llenarCredenciales("admin", "admin1234")}
            className="flex flex-col items-start rounded-xl border border-gray-200 bg-white p-2 text-left hover:border-blue-400 hover:bg-blue-50/40 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-blue-500 transition active:scale-98"
          >
            <span className="flex items-center gap-1 text-[11px] font-bold text-[#2165d5] dark:text-blue-400">
              <ShieldCheck size={12} />
              Admin
            </span>
            <span className="text-[10px] text-gray-500 dark:text-gray-400">
              admin / admin1234
            </span>
          </button>

          <button
            type="button"
            onClick={() => llenarCredenciales("marcelo", "chofer1234")}
            className="flex flex-col items-start rounded-xl border border-gray-200 bg-white p-2 text-left hover:border-emerald-400 hover:bg-emerald-50/40 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-emerald-500 transition active:scale-98"
          >
            <span className="flex items-center gap-1 text-[11px] font-bold text-[#1f6c58] dark:text-emerald-400">
              <Truck size={12} />
              Chofer
            </span>
            <span className="text-[10px] text-gray-500 dark:text-gray-400">
              marcelo / chofer1234
            </span>
          </button>
        </div>
      </div>
    </form>
  );
}
