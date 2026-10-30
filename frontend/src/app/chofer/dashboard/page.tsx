import { obtenerServiciosChofer } from "@/features/servicios/actions";
import { PortalChofer } from "@/features/servicios/components/portal-chofer";
import { requestAutenticado } from "@/lib/api/servidor";
import { exigirRol } from "@/lib/auth/guards";
import type { components } from "@/types/openapi";

export const instant = false;

export const metadata = {
  title: "Tus viajes",
  description: "Agenda de servicios asignados al chofer.",
};

export default async function ChoferDashboardPage() {
  const usuario = await exigirRol("CHOFER");

  if (usuario.id_chofer === null) {
    throw new Error("La cuenta de chofer no tiene un chofer asociado.");
  }

  const [chofer, resultadoServicios] = await Promise.all([
    requestAutenticado<components["schemas"]["ChoferRead"]>(
      `/api/choferes/${usuario.id_chofer}`,
    ),
    obtenerServiciosChofer(),
  ]);
  const fechaPartes = new Intl.DateTimeFormat("en", {
    timeZone: "America/Argentina/Buenos_Aires",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());
  const parteFecha = (tipo: string) =>
    fechaPartes.find((parte) => parte.type === tipo)?.value ?? "";
  const fechaInicial = `${parteFecha("year")}-${parteFecha("month")}-${parteFecha("day")}`;

  return (
    <PortalChofer
      nombre={chofer.nombre_completo}
      fechaInicial={fechaInicial}
      serviciosIniciales={resultadoServicios.ok ? resultadoServicios.dato : []}
      errorInicial={resultadoServicios.ok ? null : resultadoServicios.mensaje}
    />
  );
}
