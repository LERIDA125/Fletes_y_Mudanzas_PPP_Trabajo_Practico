import Link from "next/link";

type Propiedades = {
  criterio: string;
  rutaSinBusqueda: string;
};

export function EstadoVacio({ criterio, rutaSinBusqueda }: Propiedades) {
  if (criterio) {
    return (
      <div role="status" className="border-t border-linea px-4 py-12 sm:px-0">
        <p className="text-[1rem] font-semibold text-tinta">
          No hay vehículos cuya patente contenga «{criterio}».
        </p>
        <p className="mt-2 text-[0.875rem] text-tinta-media">
          Probá con menos caracteres, o volvé al listado completo.
        </p>
        <Link
          href={rutaSinBusqueda}
          className="mt-5 inline-block rounded-[4px] border border-linea bg-white px-4 py-2 text-[0.875rem] font-medium text-senal hover:border-senal"
        >
          Limpiar búsqueda
        </Link>
      </div>
    );
  }

  return (
    <div role="status" className="border-t border-linea px-4 py-12 sm:px-0">
      <p className="text-[1rem] font-semibold text-tinta">
        Todavía no hay vehículos dados de alta en el sistema.
      </p>
      <p className="mt-2 text-[0.875rem] text-tinta-media">
        Cuando registres el primero, va a aparecer acá con su patente, tipo y capacidad de
        carga.
      </p>
    </div>
  );
}
