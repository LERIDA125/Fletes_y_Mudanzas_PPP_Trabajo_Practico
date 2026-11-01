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
          ? "border-emerald-200 bg-emerald-50 text-slate-900 dark:border-[#14532d] dark:bg-[#0f2e22] dark:text-slate-100"
          : "border-amber-200 bg-amber-50 text-slate-900 dark:border-amber-800/60 dark:bg-amber-950/40 dark:text-slate-100"
      }`}
    >
      <h3 id="titulo-cotizacion" className="text-base font-semibold text-panel-texto">
        {vigente ? "Precio sugerido" : "La cotización quedó desactualizada"}
      </h3>
      <p className="mt-1 text-xs text-panel-secundario">
        {vigente
          ? `${cotizacion.descripcion_tipo_vehiculo} · ${cotizacion.horas_estimadas} h · ${cotizacion.distancia_ida_km} km de ida`
          : "Cambiaste las condiciones del viaje. Esperá la nueva cotización para continuar."}
      </p>

      <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
        <Fila etiqueta="Base por horas" valor={cotizacion.base_horas} />
        <Fila etiqueta="Base por kilómetros excedentes" valor={cotizacion.base_km} />
        <Fila etiqueta="Subtotal base" valor={cotizacion.subtotal_base} />
        {cotizacion.requiere_ayudante ? (
          <Fila etiqueta="Recargo por ayudante" valor={cotizacion.recargo_ayudante} />
        ) : null}
        {cotizacion.acceso_escalera ? (
          <Fila etiqueta="Recargo por escalera" valor={cotizacion.recargo_escalera} />
        ) : null}
        <Fila
          etiqueta="Subtotal con recargos fijos"
          valor={cotizacion.subtotal_con_fijos}
        />
        {cotizacion.zona_concurrida ? (
          <Fila
            etiqueta={`Recargo por zona concurrida (${cotizacion.porcentaje_zona_concurrida} %)`}
            valor={cotizacion.importe_recargo_zona_concurrida}
          />
        ) : null}
        {cotizacion.urgencia_mismo_dia ? (
          <Fila
            etiqueta={`Recargo por urgencia (${cotizacion.porcentaje_urgencia_mismo_dia} %)`}
            valor={cotizacion.importe_recargo_urgencia_mismo_dia}
          />
        ) : null}
        <Fila
          etiqueta="Total de recargos porcentuales"
          valor={cotizacion.total_recargos_porcentuales}
        />
      </dl>

      <p className="mt-5 flex flex-wrap items-baseline justify-between gap-2 border-t border-emerald-200 pt-4 dark:border-[#14532d]">
        <span className="font-medium text-panel-texto">Precio sugerido</span>
        <strong className="text-2xl tabular-nums text-panel-texto">
          {formatoMoneda.format(Number(cotizacion.precio_sugerido))}
        </strong>
      </p>
    </section>
  );
}

function Fila({ etiqueta, valor }: { etiqueta: string; valor: string }) {
  return (
    <div className="flex justify-between gap-4">
      <dt className="text-panel-secundario">{etiqueta}</dt>
      <dd className="tabular-nums text-panel-texto">
        {formatoMoneda.format(Number(valor))}
      </dd>
    </div>
  );
}
