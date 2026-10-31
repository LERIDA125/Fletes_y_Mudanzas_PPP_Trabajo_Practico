export function EstadoVacio() {
  return (
    <div role="status" className="px-5 py-10">
      <p className="text-base font-semibold text-panel-texto">
        Todavía no hay servicios registrados.
      </p>
      <p className="mt-2 text-sm text-panel-secundario">
        Abrí “Nuevo servicio” para cotizar y registrar el primero.
      </p>
    </div>
  );
}
