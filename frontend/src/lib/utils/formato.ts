const ZONA_DEL_NEGOCIO = "America/Argentina/Buenos_Aires";

const formatoFecha = new Intl.DateTimeFormat("es-AR", {
  timeZone: ZONA_DEL_NEGOCIO,
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

export function fechaCorta(iso: string): string {
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) {
    return "—";
  }
  return formatoFecha.format(fecha);
}

export function totalPaginas(total: number, size: number): number {
  if (size <= 0) {
    return 0;
  }
  return Math.ceil(total / size);
}

export function primeraFilaDeLaPagina(page: number, size: number): number {
  return (page - 1) * size + 1;
}

export function ultimaFilaDeLaPagina(page: number, size: number, total: number): number {
  return Math.min(page * size, total);
}
