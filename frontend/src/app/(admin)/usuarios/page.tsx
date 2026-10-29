import type { Chofer } from "@/features/choferes/types";
import type { Servicio } from "@/features/servicios/types";
import { PanelUsuarios } from "@/features/usuarios/components/panel-usuarios";
import { listarUsuariosApi, type UsuarioRead } from "@/lib/api/auth";
import { listarChoferesActivos } from "@/lib/api/choferes";
import { listarServicios } from "@/lib/api/servicios";

export default async function PaginaUsuarios() {
  let usuarios: UsuarioRead[] = [];
  let choferes: Chofer[] = [];
  let servicios: Servicio[] = [];

  try {
    const [resUsuarios, resChoferes, resServicios] = await Promise.all([
      listarUsuariosApi(),
      listarChoferesActivos(),
      listarServicios(1, 20),
    ]);
    usuarios = resUsuarios;
    choferes = resChoferes;
    servicios = resServicios.items;
  } catch {
    // Si el backend no está levantado en build-time, renderiza estado vacío seguro
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight text-[#172b4d] dark:text-white">
          Gestión de Usuarios, Multi-Admin y Auditoría
        </h2>
        <p className="mt-1 text-sm text-[#6b7a90] dark:text-[#94a3b8]">
          Administrá múltiples cuentas de dueño/administrador, creale el acceso a cada
          chofer y auditá quién realizó cada operación.
        </p>
      </div>

      <PanelUsuarios
        usuariosIniciales={usuarios}
        choferesActivos={choferes}
        serviciosRecientes={servicios}
      />
    </div>
  );
}
