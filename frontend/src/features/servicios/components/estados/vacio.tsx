export function EstadoVacio() {
  return (
    <div role="status" className="border-t border-linea px-4 py-12 sm:px-0">
      <p className="text-[1rem] font-semibold text-tinta">
        Todavía no hay servicios registrados.
      </p>
      <p className="mt-2 text-[0.875rem] text-tinta-media">
        Abrí “Nuevo servicio” para cotizar y registrar el primero.
      </p>
    </div>
  );
}
