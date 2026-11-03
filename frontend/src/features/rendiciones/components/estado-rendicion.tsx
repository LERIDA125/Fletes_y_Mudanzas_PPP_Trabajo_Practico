const ESTADOS: Record<string, { etiqueta: string; clase: string }> = {
  pendiente: {
    etiqueta: "Pendiente",
    clase: "bg-[#fff4e5] text-[#b86a16] dark:bg-[#3d2914] dark:text-[#fbbf24]",
  },
  "en revision": {
    etiqueta: "En revisión",
    clase: "bg-[#e9f4ff] text-[#2879bd] dark:bg-[#1a3356] dark:text-[#60a5fa]",
  },
  aprobada: {
    etiqueta: "Aprobada",
    clase: "bg-[#e9f8ef] text-[#248952] dark:bg-[#163827] dark:text-[#4ade80]",
  },
};

export function EtiquetaEstadoRendicion({ estado }: { estado: string }) {
  const configuracion = ESTADOS[estado] ?? {
    etiqueta: estado,
    clase: "bg-[#f1f3f6] text-[#62738a] dark:bg-[#1e2c44] dark:text-[#cbd5e1]",
  };

  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold ${configuracion.clase}`}
    >
      {configuracion.etiqueta}
    </span>
  );
}
