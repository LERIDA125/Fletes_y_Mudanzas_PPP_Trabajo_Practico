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
      className={`mt-5 rounded-xl border p-4 transition-colors ${
        vigente
          ? "border-emerald-200 bg-emerald-50/90 text-slate-900 dark:border-emerald-800/60 dark:bg-emerald-950/40 dark:text-slate-100"
          : "border-amber-200 bg-amber-50/90 text-slate-900 dark:border-amber-800/60 dark:bg-amber-950/40 dark:text-slate-100"
      }`}
    >
      <h3
        id="titulo-cotizacion"
        className={`text-base font-semibold ${
          vigente
            ? "text-emerald-950 dark:text-emerald-200"
            : "text-amber-950 dark:text-amber-200"
        }`}
      >
        {vigente ? "Cotización estimada" : "La cotización quedó desactualizada"}
      </h3>
      <p
        className={`mt-1 text-sm ${
          vigente
            ? "text-emerald-800/90 dark:text-emerald-300/80"
            : "text-amber-800/90 dark:text-amber-300/80"
        }`}
      >
        {vigente
          ? "El importe es una estimación. El servidor vuelve a calcularlo al registrar el servicio."
          : "Cambiaste los datos del viaje. Solicitá una nueva cotización para continuar."}
      </p>

      <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
        <div className="flex justify-between gap-4">
          <dt className="text-slate-600 dark:text-slate-300">Tipo de vehículo</dt>
          <dd className="text-right font-medium text-slate-900 dark:text-white">
            {cotizacion.descripcion_tipo_vehiculo}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-600 dark:text-slate-300">Horas estimadas</dt>
          <dd className="tabular-nums font-medium text-slate-900 dark:text-white">
            {cotizacion.horas_estimadas}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-600 dark:text-slate-300">Distancia total</dt>
          <dd className="tabular-nums font-medium text-slate-900 dark:text-white">
            {cotizacion.distancia_total_km} km
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-600 dark:text-slate-300">Kilómetros excedentes</dt>
          <dd className="tabular-nums font-medium text-slate-900 dark:text-white">
            {cotizacion.km_excedente} km
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-600 dark:text-slate-300">Tarifa por hora</dt>
          <dd className="tabular-nums font-medium text-slate-900 dark:text-white">
            {formatoMoneda.format(Number(cotizacion.tarifa_hora_base))}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-600 dark:text-slate-300">Tarifa por km excedente</dt>
          <dd className="tabular-nums font-medium text-slate-900 dark:text-white">
            {formatoMoneda.format(Number(cotizacion.tarifa_km_excedente))}
          </dd>
        </div>
      </dl>

      <p
        className={`mt-5 flex flex-wrap items-baseline justify-between gap-2 border-t pt-4 ${
          vigente
            ? "border-emerald-200 dark:border-emerald-800/60"
            : "border-amber-200 dark:border-amber-800/60"
        }`}
      >
        <span className="font-medium text-slate-800 dark:text-slate-200">
          Precio estimado
        </span>
        <strong
          className={`text-2xl tabular-nums ${
            vigente
              ? "text-emerald-950 dark:text-emerald-300"
              : "text-amber-950 dark:text-amber-300"
          }`}
        >
          {formatoMoneda.format(Number(cotizacion.precio_final))}
        </strong>
      </p>
    </section>
  );
}
