"use client";

import { AlertCircle, Camera, Check, Loader2, Upload, X } from "lucide-react";
import { useState } from "react";

import { finalizarViajeChofer } from "@/features/servicios/actions";
import type { Servicio } from "@/features/servicios/types";
import { formatearSaldo } from "@/lib/utils/formato";

interface ModalFinalizarViajeProps {
  servicio: Servicio;
  abierto: boolean;
  onCerrar: () => void;
  onExito?: (servicioActualizado: Servicio) => void;
}

/**
 * Comprime y redimensiona la imagen en el cliente para asegurar un peso liviano
 * antes de enviarla como Data URL Base64 a la API.
 */
async function procesarFotoRemito(archivo: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const lector = new FileReader();
    lector.onerror = () => reject(new Error("No se pudo leer el archivo de imagen"));
    lector.onload = (evento) => {
      const img = new Image();
      img.onerror = () => reject(new Error("Formato de imagen no compatible"));
      img.onload = () => {
        const MAX_DIM = 1280;
        let { width, height } = img;
        if (width > MAX_DIM || height > MAX_DIM) {
          if (width > height) {
            height = Math.round((height * MAX_DIM) / width);
            width = MAX_DIM;
          } else {
            width = Math.round((width * MAX_DIM) / height);
            height = MAX_DIM;
          }
        }

        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        if (!ctx) {
          return resolve(evento.target?.result as string);
        }
        ctx.drawImage(img, 0, 0, width, height);
        // Calidad 0.82 JPEG
        const dataUrl = canvas.toDataURL("image/jpeg", 0.82);
        resolve(dataUrl);
      };
      img.src = evento.target?.result as string;
    };
    lector.readAsDataURL(archivo);
  });
}

export function ModalFinalizarViaje({
  servicio,
  abierto,
  onCerrar,
  onExito,
}: ModalFinalizarViajeProps) {
  const [montoCobrado, setMontoCobrado] = useState<string>(
    String(servicio.precio_total || ""),
  );
  const [fotoDataUrl, setFotoDataUrl] = useState<string | null>(null);
  const [procesandoFoto, setProcesandoFoto] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!abierto) return null;

  async function handleSeleccionarArchivo(e: React.ChangeEvent<HTMLInputElement>) {
    const archivo = e.target.files?.[0];
    if (!archivo) return;

    setError(null);
    setProcesandoFoto(true);
    try {
      const dataUrl = await procesarFotoRemito(archivo);
      setFotoDataUrl(dataUrl);
    } catch {
      setError("No se pudo procesar la imagen seleccionada. Intentá nuevamente.");
    } finally {
      setProcesandoFoto(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!fotoDataUrl) {
      setError("Es obligatorio adjuntar la foto del remito firmado.");
      return;
    }

    const montoLimpio = montoCobrado.replace(",", ".");
    const montoNum = Number(montoLimpio);
    if (isNaN(montoNum) || montoNum < 0) {
      setError("Ingresá un monto cobrado válido mayor o igual a 0.");
      return;
    }

    setEnviando(true);
    try {
      const resultado = await finalizarViajeChofer(servicio.id_servicio, {
        monto_cobrado_real: montoNum,
        foto_remito_url: fotoDataUrl,
      });

      if (!resultado.ok) {
        setError(resultado.mensaje);
        return;
      }

      onExito?.(resultado.dato);
      onCerrar();
    } catch {
      setError("Ocurrió un error inesperado al finalizar el servicio.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="titulo-modal-finalizar"
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 p-0 backdrop-blur-xs sm:items-center sm:p-4"
    >
      <div className="w-full max-w-md rounded-t-[1.8rem] bg-white p-5 shadow-2xl sm:rounded-2xl sm:p-6">
        <header className="flex items-start justify-between border-b border-[#edf1ef] pb-3">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#1f6c58]">
              Prueba de Entrega (POD)
            </span>
            <h3
              id="titulo-modal-finalizar"
              className="mt-0.5 text-base font-bold text-[#1a3831]"
            >
              Finalizar viaje #{servicio.id_servicio}
            </h3>
            <p className="text-xs text-[#6e857c]">{servicio.razon_social_cliente}</p>
          </div>
          <button
            type="button"
            onClick={onCerrar}
            disabled={enviando}
            aria-label="Cerrar modal"
            className="rounded-lg p-1 text-[#8b9e97] hover:bg-[#f1f6f4] hover:text-[#23433b]"
          >
            <X size={18} />
          </button>
        </header>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {error && (
            <div
              role="alert"
              className="flex items-start gap-2 rounded-xl border border-[#f5c6cb] bg-[#fdf2f2] p-3 text-xs text-[#a94442]"
            >
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* 1. Captura de Foto del Remito */}
          <div>
            <label className="block text-xs font-bold text-[#23433b]">
              Foto del remito firmado <span className="text-red-500">*</span>
            </label>
            <p className="mt-0.5 text-[11px] text-[#788e85]">
              Tomá una foto clara donde se vea la firma o sello de conformidad del
              cliente.
            </p>

            {fotoDataUrl ? (
              <div className="relative mt-2 overflow-hidden rounded-xl border border-[#d2e2dc] bg-[#f8faf9]">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={fotoDataUrl}
                  alt="Previsualización del remito firmado"
                  className="max-h-48 w-full object-contain bg-black/5"
                />
                <button
                  type="button"
                  onClick={() => setFotoDataUrl(null)}
                  disabled={enviando}
                  className="absolute top-2 right-2 flex items-center gap-1 rounded-full bg-black/70 px-2.5 py-1 text-[11px] font-semibold text-white backdrop-blur-xs hover:bg-black/90"
                >
                  <X size={13} />
                  <span>Cambiar foto</span>
                </button>
              </div>
            ) : (
              <label className="mt-2 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-[#b3cbbf] bg-[#f7fbf9] p-4 text-center transition hover:border-[#1f6c58] hover:bg-[#edf6f2]">
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleSeleccionarArchivo}
                  disabled={procesandoFoto || enviando}
                  className="sr-only"
                />
                {procesandoFoto ? (
                  <div className="flex items-center gap-2 text-xs font-semibold text-[#1f6c58]">
                    <Loader2 size={18} className="animate-spin" />
                    <span>Procesando foto...</span>
                  </div>
                ) : (
                  <>
                    <div className="grid size-11 place-items-center rounded-full bg-[#e3efe9] text-[#1f6c58]">
                      <Camera size={22} />
                    </div>
                    <span className="mt-2 text-xs font-bold text-[#20443a]">
                      Sacar foto o subir comprobante
                    </span>
                    <span className="mt-0.5 flex items-center gap-1 text-[10px] text-[#718b80]">
                      <Upload size={11} /> Cámara o galería
                    </span>
                  </>
                )}
              </label>
            )}
          </div>

          {/* 2. Confirmación de Monto Cobrado Real */}
          <div>
            <div className="flex items-center justify-between">
              <label
                htmlFor="monto-cobrado-input"
                className="text-xs font-bold text-[#23433b]"
              >
                Monto real cobrado en mano <span className="text-red-500">*</span>
              </label>
              <span className="text-[10px] text-[#718b80]">
                Cotizado: {formatearSaldo(Number(servicio.precio_total))}
              </span>
            </div>
            <div className="relative mt-1.5">
              <span className="absolute top-1/2 left-3 -translate-y-1/2 text-xs font-bold text-[#627d73]">
                $
              </span>
              <input
                id="monto-cobrado-input"
                type="number"
                step="any"
                min="0"
                value={montoCobrado}
                onChange={(e) => setMontoCobrado(e.target.value)}
                disabled={enviando}
                required
                className="w-full rounded-xl border border-[#c5d8cf] bg-white py-2.5 pr-3 pl-7 text-sm font-bold text-[#1f4239] shadow-xs focus:border-[#1f6c58] focus:ring-1 focus:ring-[#1f6c58] focus:outline-hidden"
              />
            </div>
            <p className="mt-1 text-[10px] text-[#718b80]">
              Si hubo peajes, esperas o cambio de ruta, ajustá el valor efectivamente
              recibido.
            </p>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onCerrar}
              disabled={enviando}
              className="rounded-xl border border-[#cbd8d2] px-4 py-2.5 text-xs font-semibold text-[#546a62] hover:bg-[#f4f7f6]"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={enviando || procesandoFoto || !fotoDataUrl}
              className="flex items-center gap-1.5 rounded-xl bg-[#1f6c58] px-4 py-2.5 text-xs font-bold text-white shadow-md transition hover:bg-[#185545] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {enviando ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  <span>Finalizando viaje...</span>
                </>
              ) : (
                <>
                  <Check size={14} />
                  <span>Confirmar y Rendir</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
