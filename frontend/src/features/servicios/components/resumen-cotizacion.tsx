import type { Cotizacion } from "@/features/servicios/types";

const formatoMoneda = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
});

type Propiedades = {
  cotizacion: Cotizacion;
  vigente: boolean;
};

export function ResumenCotizacion({ cotizacion, vigente }: Propiedades) {
  return (
    <section
      aria-labelledby="titulo-cotizacion"
      aria-live="polite"
      className={`mt-6 border-l-4 p-4 ${
        vigente ? "border-senal bg-white" : "border-alerta bg-white"
      }`}
    >
      <h3 id="titulo-cotizacion" className="text-[1rem] font-semibold text-tinta">
        {vigente ? "Cotización estimada" : "La cotización quedó desactualizada"}
      </h3>
      <p className="mt-1 text-[0.875rem] text-tinta-media">
        {vigente
          ? "El importe es una estimación. El servidor vuelve a calcularlo al registrar el servicio."
          : "Cambiaste los datos del viaje. Solicitá una nueva cotización para continuar."}
      </p>

      <dl className="mt-4 grid gap-x-6 gap-y-2 text-[0.875rem] sm:grid-cols-2">
        <div className="flex justify-between gap-4">
          <dt className="text-tinta-media">Tipo de vehículo</dt>
          <dd className="text-right font-medium text-tinta">
            {cotizacion.descripcion_tipo_vehiculo}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-tinta-media">Horas estimadas</dt>
          <dd className="tabular-nums text-tinta">{cotizacion.horas_estimadas}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-tinta-media">Distancia total</dt>
          <dd className="tabular-nums text-tinta">{cotizacion.distancia_total_km} km</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-tinta-media">Kilómetros excedentes</dt>
          <dd className="tabular-nums text-tinta">{cotizacion.km_excedente} km</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-tinta-media">Tarifa por hora</dt>
          <dd className="tabular-nums text-tinta">
            {formatoMoneda.format(Number(cotizacion.tarifa_hora_base))}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-tinta-media">Tarifa por km excedente</dt>
          <dd className="tabular-nums text-tinta">
            {formatoMoneda.format(Number(cotizacion.tarifa_km_excedente))}
          </dd>
        </div>
      </dl>

      <p className="mt-5 flex flex-wrap items-baseline justify-between gap-2 border-t border-linea pt-4">
        <span className="font-medium text-tinta">Precio estimado</span>
        <strong className="text-[1.5rem] tabular-nums text-tinta">
          {formatoMoneda.format(Number(cotizacion.precio_final))}
        </strong>
      </p>
    </section>
  );
}
