import type { Cotizacion } from "@/features/servicios/types";

const formatoMoneda = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
});

type Propiedades = {
  cotizacion: Cotizacion;
};

export function ResumenCotizacion({ cotizacion }: Propiedades) {
  return (
    <section
      aria-labelledby="titulo-cotizacion"
      className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 dark:border-[#14532d] dark:bg-[#0f2e22]"
    >
      <h3 id="titulo-cotizacion" className="text-base font-semibold text-panel-texto">
        Precio sugerido
      </h3>
      <p className="mt-1 text-xs text-panel-secundario">
        {cotizacion.descripcion_tipo_vehiculo} · {cotizacion.horas_estimadas} h ·{" "}
        {cotizacion.km_estimados} km
      </p>

      <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
        <Fila etiqueta="Base por horas" valor={cotizacion.base_horas} />
        <Fila etiqueta="Base por kilómetros" valor={cotizacion.base_km} />
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
