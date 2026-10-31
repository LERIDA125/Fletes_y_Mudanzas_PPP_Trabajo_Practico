"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, useWatch } from "react-hook-form";

import { FormularioCotizacion } from "@/features/cotizaciones/components/formulario-cotizacion";
import {
  DATOS_COTIZACION_INICIALES,
  esquemaDatosCotizacion,
  type DatosCotizacion,
  type ValoresDatosCotizacion,
} from "@/features/cotizaciones/schemas/cotizacion";
import type { TipoVehiculoCotizacion } from "@/features/cotizaciones/types";

type Propiedades = {
  tiposVehiculo: TipoVehiculoCotizacion[];
};

export function Cotizador({ tiposVehiculo }: Propiedades) {
  const { control, setValue } = useForm<DatosCotizacion, unknown, ValoresDatosCotizacion>(
    {
      resolver: zodResolver(esquemaDatosCotizacion),
      defaultValues: DATOS_COTIZACION_INICIALES,
    },
  );
  const valores = useWatch({ control });

  const datos: DatosCotizacion = {
    id_tipo_vehiculo: valores.id_tipo_vehiculo ?? "",
    horas_estimadas: valores.horas_estimadas ?? "1",
    km_estimados: valores.km_estimados ?? "0",
    requiere_ayudante: valores.requiere_ayudante ?? false,
    acceso_escalera: valores.acceso_escalera ?? false,
    zona_concurrida: valores.zona_concurrida ?? false,
    urgencia_mismo_dia: valores.urgencia_mismo_dia ?? false,
  };

  function cambiarDatos(parcial: Partial<DatosCotizacion>) {
    if (parcial.id_tipo_vehiculo !== undefined) {
      setValue("id_tipo_vehiculo", parcial.id_tipo_vehiculo, { shouldDirty: true });
    }
    if (parcial.horas_estimadas !== undefined) {
      setValue("horas_estimadas", parcial.horas_estimadas, { shouldDirty: true });
    }
    if (parcial.km_estimados !== undefined) {
      setValue("km_estimados", parcial.km_estimados, { shouldDirty: true });
    }
    if (parcial.requiere_ayudante !== undefined) {
      setValue("requiere_ayudante", parcial.requiere_ayudante, {
        shouldDirty: true,
      });
    }
    if (parcial.acceso_escalera !== undefined) {
      setValue("acceso_escalera", parcial.acceso_escalera, { shouldDirty: true });
    }
    if (parcial.zona_concurrida !== undefined) {
      setValue("zona_concurrida", parcial.zona_concurrida, { shouldDirty: true });
    }
    if (parcial.urgencia_mismo_dia !== undefined) {
      setValue("urgencia_mismo_dia", parcial.urgencia_mismo_dia, {
        shouldDirty: true,
      });
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
      <section className="rounded-xl border border-panel-borde/70 bg-panel-superficie p-5 sm:p-6">
        <div className="border-b border-panel-borde/60 pb-4">
          <h3 className="text-lg font-semibold text-panel-texto">Nueva cotización</h3>
          <p className="mt-1 text-sm text-panel-secundario">
            El servidor calcula el importe con las tarifas vigentes.
          </p>
        </div>

        {tiposVehiculo.length === 0 ? (
          <p role="status" className="mt-5 text-sm text-panel-secundario">
            No hay tipos de vehículo activos para cotizar. Cargá uno desde Vehículos.
          </p>
        ) : (
          <div className="mt-5">
            <FormularioCotizacion
              tiposVehiculo={tiposVehiculo}
              datos={datos}
              onDatosChange={cambiarDatos}
              incluirPrecioAcordado={false}
            />
          </div>
        )}
      </section>

      <aside className="flex flex-col justify-between rounded-xl bg-panel-primario p-5 text-white">
        <div>
          <p className="text-sm text-white/75">Cotización informativa</p>
          <p className="mt-2 text-2xl font-semibold">Sin guardar un servicio</p>
        </div>
        <p className="mt-8 border-t border-white/20 pt-4 text-sm leading-relaxed text-white/80">
          Los cambios se calculan automáticamente. El importe mostrado es el precio
          sugerido que devuelve el sistema.
        </p>
      </aside>
    </div>
  );
}
