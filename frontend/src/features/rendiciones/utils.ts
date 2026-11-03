import { formatearSaldo } from "@/lib/utils/formato";

export function formatearFecha(fecha: string): string {
  const [anio, mes, dia] = fecha.split("-");
  if (!anio || !mes || !dia) {
    return "—";
  }
  return `${dia}/${mes}/${anio}`;
}

export function formatearMonto(valor: string | number): string {
  return formatearSaldo(Number(valor));
}
