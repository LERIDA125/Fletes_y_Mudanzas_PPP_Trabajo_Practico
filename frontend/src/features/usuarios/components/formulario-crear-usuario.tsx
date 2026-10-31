"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { CheckCircle2, UserPlus } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm, useWatch } from "react-hook-form";

import type { Chofer } from "@/features/choferes/types";
import { crearUsuario } from "@/features/usuarios/actions";
import { esquemaUsuario, type ValoresUsuario } from "@/features/usuarios/schemas/usuario";

const VALORES_INICIALES: ValoresUsuario = {
  username: "",
  password: "",
  rol: "ADMIN",
  id_chofer: null,
};

export function FormularioCrearUsuario({ choferes }: { choferes: Chofer[] }) {
  const router = useRouter();
  const [mensaje, setMensaje] = useState("");
  const [exito, setExito] = useState("");
  const [enviando, setEnviando] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    control,
    setValue,
    formState: { errors },
  } = useForm<ValoresUsuario>({
    resolver: zodResolver(esquemaUsuario),
    defaultValues: VALORES_INICIALES,
  });

  const rol = useWatch({ control, name: "rol" });

  useEffect(() => {
    if (rol === "ADMIN") {
      setValue("id_chofer", null);
    }
  }, [rol, setValue]);

  async function guardar(valores: ValoresUsuario) {
    setMensaje("");
    setExito("");
    setEnviando(true);

    try {
      const respuesta = await crearUsuario({
        username: valores.username,
        password: valores.password,
        rol: valores.rol,
        id_chofer: valores.rol === "CHOFER" ? (valores.id_chofer ?? null) : null,
      });

      if (!respuesta.ok) {
        setMensaje(respuesta.mensaje);
        return;
      }

      setExito(
        `Cuenta "${respuesta.usuario.username}" creada con rol ${respuesta.usuario.rol}.`,
      );
      reset(VALORES_INICIALES);
      router.refresh();
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form className="flex flex-col gap-5" noValidate onSubmit={handleSubmit(guardar)}>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label
            htmlFor="username"
            className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
          >
            Usuario
          </label>
          <input
            id="username"
            autoComplete="off"
            autoCapitalize="none"
            spellCheck={false}
            aria-invalid={Boolean(errors.username)}
            aria-describedby={errors.username ? "username-error" : undefined}
            {...register("username")}
            className={claseControl}
            placeholder="juan.perez"
          />
          {errors.username ? (
            <p id="username-error" className="mt-1 text-xs text-alerta">
              {errors.username.message}
            </p>
          ) : null}
        </div>

        <div>
          <label
            htmlFor="password"
            className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
          >
            Contraseña
          </label>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            aria-invalid={Boolean(errors.password)}
            aria-describedby={errors.password ? "password-error" : "password-ayuda"}
            {...register("password")}
            className={claseControl}
            placeholder="Mínimo 12 caracteres"
          />
          {errors.password ? (
            <p id="password-error" className="mt-1 text-xs text-alerta">
              {errors.password.message}
            </p>
          ) : (
            <p id="password-ayuda" className="mt-1 text-[11px] text-panel-secundario">
              Entre 12 y 128 caracteres.
            </p>
          )}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label
            htmlFor="rol"
            className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
          >
            Rol
          </label>
          <select
            id="rol"
            aria-invalid={Boolean(errors.rol)}
            {...register("rol")}
            className={claseControl}
          >
            <option value="ADMIN">Administrador</option>
            <option value="CHOFER">Chofer</option>
          </select>
          {errors.rol ? (
            <p className="mt-1 text-xs text-alerta">{errors.rol.message}</p>
          ) : null}
        </div>

        {rol === "CHOFER" ? (
          <div>
            <label
              htmlFor="id_chofer"
              className="block text-xs font-semibold uppercase tracking-wider text-panel-secundario"
            >
              Chofer asociado
            </label>
            <select
              id="id_chofer"
              aria-invalid={Boolean(errors.id_chofer)}
              aria-describedby={errors.id_chofer ? "id_chofer-error" : undefined}
              {...register("id_chofer", {
                setValueAs: (valor) => (valor === "" ? null : Number(valor)),
              })}
              className={claseControl}
            >
              <option value="" disabled>
                Elegí un chofer activo
              </option>
              {choferes.map((chofer) => (
                <option key={chofer.id} value={chofer.id}>
                  {chofer.nombre_completo}
                </option>
              ))}
            </select>
            {errors.id_chofer ? (
              <p id="id_chofer-error" className="mt-1 text-xs text-alerta">
                {errors.id_chofer.message}
              </p>
            ) : choferes.length === 0 ? (
              <p className="mt-1 text-[11px] text-panel-secundario">
                No hay choferes activos. Crealo primero en la sección Choferes.
              </p>
            ) : null}
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-panel-borde/80 bg-panel-suave/40 px-4 py-3 text-[11px] leading-5 text-panel-secundario">
            Una cuenta ADMIN no se vincula a un chofer y puede coexistir con otras cuentas
            administrativas activas.
          </div>
        )}
      </div>

      {mensaje ? (
        <p
          role="alert"
          className="rounded-xl border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm font-medium text-red-700 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-300"
        >
          {mensaje}
        </p>
      ) : null}

      {exito ? (
        <p
          role="status"
          className="flex items-start gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-3.5 py-2.5 text-sm font-medium text-emerald-700 dark:border-emerald-900/60 dark:bg-emerald-950/40 dark:text-emerald-300"
        >
          <CheckCircle2 aria-hidden="true" size={17} className="mt-0.5 shrink-0" />
          {exito}
        </p>
      ) : null}

      <div className="flex justify-end pt-1">
        <button
          type="submit"
          disabled={enviando}
          className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-panel-primario px-4 text-sm font-bold text-white shadow-md transition-all hover:bg-slate-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-panel-azul disabled:cursor-not-allowed disabled:opacity-50"
        >
          <UserPlus aria-hidden="true" size={16} />
          {enviando ? "Creando cuenta…" : "Crear usuario"}
        </button>
      </div>
    </form>
  );
}

const claseControl =
  "mt-1 block min-h-10 w-full rounded-lg border border-panel-borde/80 bg-white px-3 py-2 text-sm text-panel-texto shadow-xs transition-colors focus:border-panel-azul focus:ring-2 focus:ring-panel-azul/20 focus-visible:outline-none dark:bg-[#0d1626] dark:text-white";
