import Link from "next/link";

export function EstadoVacioRendiciones({
  criterio,
  pagina,
}: {
  criterio: string;
  pagina: number;
}) {
  if (criterio) {
    return (
      <div role="status" className="py-10 text-center">
        <p className="text-base font-semibold text-[#172b4d] dark:text-white">
          No hay rendiciones que coincidan con «{criterio}».
        </p>
        <p className="mt-2 text-sm text-[#7f8da1] dark:text-[#94a3b8]">
          Probá con otro código, chofer o cliente.
        </p>
        <Link
          href="/rendiciones"
          className="mt-5 inline-flex min-h-10 items-center justify-center rounded-lg border border-[#dfe6ef] bg-white px-4 text-sm font-medium text-[#62738a] shadow-xs hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:bg-[#111c2e] dark:text-[#94a3b8] dark:hover:bg-[#16253d]"
        >
          Limpiar búsqueda
        </Link>
      </div>
    );
  }

  if (pagina > 1) {
    return (
      <div role="status" className="py-10 text-center">
        <p className="text-base font-semibold text-[#172b4d] dark:text-white">
          La página {pagina} no tiene rendiciones.
        </p>
        <p className="mt-2 text-sm text-[#7f8da1] dark:text-[#94a3b8]">
          El listado no llega tan lejos. Volvé a empezar desde el principio.
        </p>
        <Link
          href="/rendiciones"
          className="mt-5 inline-flex min-h-10 items-center justify-center rounded-lg border border-[#dfe6ef] bg-white px-4 text-sm font-medium text-[#62738a] shadow-xs hover:bg-[#f7f9fc] dark:border-[#1e2c44] dark:bg-[#111c2e] dark:text-[#94a3b8] dark:hover:bg-[#16253d]"
        >
          Ir a la primera página
        </Link>
      </div>
    );
  }

  return (
    <div role="status" className="py-10 text-center">
      <p className="text-base font-semibold text-[#172b4d] dark:text-white">
        Todavía no hay rendiciones registradas.
      </p>
      <p className="mt-2 text-sm text-[#7f8da1] dark:text-[#94a3b8]">
        Cuando cierres un servicio con chofer, vas a poder registrar su rendición desde
        «Nueva rendición».
      </p>
    </div>
  );
}
