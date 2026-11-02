"use client";

import { Camera, Check, DollarSign, Loader2, Upload, X } from "lucide-react";
import { useState, useTransition, type ChangeEvent, type FormEvent } from "react";

import { finalizarViajeChofer } from "@/features/servicios/actions";
import type { Servicio } from "@/features/servicios/types";
import { formatearSaldo } from "@/lib/utils/formato";

interface Props {
  servicio: Servicio;
  abierto: boolean;
  alCerrar: () => void;
  alFinalizar?: (servicioActualizado: Servicio) => void;
}

export function ModalFinalizarViaje({ servicio, abierto, alCerrar, alFinalizar }: Props) {
  const [pendiente, startTransition] = useTransition();
  const [fotoDataUrl, setFotoDataUrl] = useState<string | null>(null);
  const [nombreArchivo, setNombreArchivo] = useState<string | null>(null);
  const [montoCobrado, setMontoCobrado] = useState<string>(
    String(Number(servicio.precio_total) || 0),
  );
  const [error, setError] = useState<string | null>(null);

  if (!abierto) return null;

  function procesarArchivo(file: File) {
    if (!file.type.startsWith("image/")) {
      setError("El archivo seleccionado debe ser una imagen (JPG, PNG, etc.)");
      return;
    }
    setError(null);
    setNombreArchivo(file.name);

    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      // Comprimir opcionalmente con canvas para no saturar memoria
      const img = new Image();
      img.onload = () => {
        const maxDim = 1200;
        let width = img.width;
        let height = img.height;
        if (width > maxDim || height > maxDim) {
          if (width > height) {
            height = Math.round((height * maxDim) / width);
            width = maxDim;
          } else {
            width = Math.round((width * maxDim) / height);
            height = maxDim;
          }
        }
        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        if (ctx) {
          ctx.drawImage(img, 0, 0, width, height);
          setFotoDataUrl(canvas.toDataURL("image/jpeg", 0.82));
        } else {
          setFotoDataUrl(result);
        }
      };
      img.src = result;
    };
    reader.readAsDataURL(file);
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      procesarArchivo(file);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!fotoDataUrl) {
      setError(
        "Es obligatorio adjuntar la foto del remito firmado para finalizar el viaje.",
      );
      return;
    }
    const montoNum = parseFloat(montoCobrado.replace(",", "."));
    if (isNaN(montoNum) || montoNum < 0) {
      setError("Ingresá un monto cobrado válido mayor o igual a 0.");
      return;
    }

    setError(null);
    startTransition(async () => {
      const res = await finalizarViajeChofer(servicio.id_servicio, {
        foto_remito_url: fotoDataUrl,
        monto_cobrado_real: montoNum,
      });

      if (res.ok) {
        if (alFinalizar) {
          alFinalizar(res.dato);
        }
        alCerrar();
      } else {
        setError(res.mensaje);
      }
    });
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-finalizar-titulo"
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 p-0 sm:items-center sm:p-4 backdrop-blur-xs animate-in fade-in duration-200"
    >
      <div className="w-full max-w-lg rounded-t-3xl bg-white p-5 shadow-2xl sm:rounded-3xl dark:bg-[#0f172a] border border-[#dce9e4] dark:border-[#1e293b] max-h-[90dvh] overflow-y-auto">
        <div className="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-gray-800">
          <div>
            <h2
              id="modal-finalizar-titulo"
              className="text-lg font-bold text-[#193f3a] dark:text-white"
            >
              Finalizar Viaje #{servicio.id_servicio}
            </h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {servicio.razon_social_cliente}
            </p>
          </div>
          <button
            type="button"
            onClick={alCerrar}
            disabled={pendiente}
            className="rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800 transition"
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {error && (
            <div
              role="alert"
              className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700 dark:border-rose-900/60 dark:bg-rose-950/40 dark:text-rose-300"
            >
              {error}
            </div>
          )}

          {/* Sección Prueba de Entrega (POD): Foto del Remito */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-[#26423b] dark:text-gray-300 mb-1.5">
              1. Foto del Remito Firmado (Obligatorio)
            </label>
            <p className="text-[11px] text-gray-500 dark:text-gray-400 mb-2.5">
              Tomá una foto clara del remito de papel con la firma del cliente al pie.
            </p>

            {fotoDataUrl ? (
              <div className="relative rounded-2xl border border-[#b2d5c7] bg-[#f0f8f5] p-3 text-center dark:border-emerald-800/60 dark:bg-emerald-950/20">
                <div className="relative mx-auto max-h-48 overflow-hidden rounded-xl border border-[#9dcfbe]">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={fotoDataUrl}
                    alt="Remito firmado"
                    className="w-full max-h-48 object-contain bg-black/5"
                  />
                </div>
                <div className="mt-2.5 flex items-center justify-between text-xs px-1">
                  <span className="font-semibold text-[#1f6c58] flex items-center gap-1 truncate max-w-[200px]">
                    <Check size={14} className="text-emerald-600" />
                    {nombreArchivo ?? "Foto cargada"}
                  </span>
                  <label
                    htmlFor="captura-remito-cambiar"
                    className="cursor-pointer font-bold text-[#2165d5] hover:underline"
                  >
                    Cambiar foto
                    <input
                      id="captura-remito-cambiar"
                      type="file"
                      accept="image/*"
                      capture="environment"
                      className="sr-only"
                      onChange={handleFileChange}
                    />
                  </label>
                </div>
              </div>
            ) : (
              <div className="rounded-2xl border-2 border-dashed border-[#b6d3c8] bg-[#f9fcfb] p-5 text-center dark:border-[#334155] dark:bg-[#1e293b]/40">
                <div className="mx-auto grid size-12 place-items-center rounded-full bg-[#e3f1eb] text-[#28745f] dark:bg-emerald-900/40 dark:text-emerald-400">
                  <Camera size={24} />
                </div>
                <p className="mt-2 text-xs font-bold text-[#20443c] dark:text-gray-200">
                  Adjuntar o tomar foto con la cámara
                </p>
                <p className="mt-0.5 text-[10px] text-gray-400">
                  Formatos aceptados: JPG, PNG, WebP
                </p>

                <div className="mt-3.5 flex flex-col sm:flex-row gap-2 justify-center">
                  <label
                    htmlFor="captura-remito-camara"
                    className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-[#1f6c58] px-4 py-2.5 text-xs font-bold text-white shadow-sm hover:bg-[#185948] cursor-pointer transition active:scale-95"
                  >
                    <Camera size={14} />
                    Abrir Cámara
                    <input
                      id="captura-remito-camara"
                      type="file"
                      accept="image/*"
                      capture="environment"
                      className="sr-only"
                      onChange={handleFileChange}
                    />
                  </label>

                  <label
                    htmlFor="captura-remito-archivo"
                    className="inline-flex items-center justify-center gap-1.5 rounded-xl border border-gray-300 bg-white px-3 py-2.5 text-xs font-semibold text-gray-700 hover:bg-gray-50 cursor-pointer transition dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
                  >
                    <Upload size={14} />
                    Elegir de galería
                    <input
                      id="captura-remito-archivo"
                      type="file"
                      accept="image/*"
                      className="sr-only"
                      onChange={handleFileChange}
                    />
                  </label>
                </div>
              </div>
            )}
          </div>

          {/* Sección Rendición Económica: Monto Cobrado Real */}
          <div className="rounded-2xl border border-amber-200/80 bg-amber-50/50 p-3.5 dark:border-amber-900/50 dark:bg-amber-950/20">
            <div className="flex items-center justify-between text-xs text-amber-900 dark:text-amber-300 mb-1">
              <span className="font-bold flex items-center gap-1">
                <DollarSign size={14} />
                2. Dinero Cobrado en Mano
              </span>
              <span className="text-[11px] text-amber-700 dark:text-amber-400">
                Cotizado: {formatearSaldo(Number(servicio.precio_total))}
              </span>
            </div>
            <p className="text-[11px] text-amber-800/80 dark:text-amber-300/80 mb-2.5">
              Confirmá o editá el importe real en efectivo que cobraste del cliente para
              rendir en caja:
            </p>

            <div className="relative">
              <span className="absolute top-1/2 left-3 -translate-y-1/2 text-sm font-bold text-gray-500">
                $
              </span>
              <input
                type="number"
                step="0.01"
                min="0"
                required
                value={montoCobrado}
                onChange={(e) => setMontoCobrado(e.target.value)}
                className="w-full rounded-xl border border-amber-300 bg-white py-2 pr-3 pl-8 text-base font-bold text-gray-900 shadow-xs focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 dark:border-amber-700 dark:bg-gray-900 dark:text-white"
                placeholder="0.00"
              />
            </div>
          </div>

          {/* Botones de acción */}
          <div className="pt-2 flex items-center gap-2">
            <button
              type="button"
              onClick={alCerrar}
              disabled={pendiente}
              className="flex-1 rounded-xl border border-gray-200 py-3 text-xs font-semibold text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={pendiente || !fotoDataUrl}
              className="flex-2 inline-flex items-center justify-center gap-2 rounded-xl bg-[#1f6c58] py-3 text-xs font-bold text-white shadow-md hover:bg-[#185948] transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {pendiente ? (
                <>
                  <Loader2 size={15} className="animate-spin" />
                  Finalizando viaje…
                </>
              ) : (
                <>
                  <Check size={16} />
                  Finalizar Viaje y Rendir
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
