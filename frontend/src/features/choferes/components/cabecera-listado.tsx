type Propiedades = {
  titulo: string;
  total: number;
  paginas: number;
};

export function CabeceraListado({ titulo, total, paginas }: Propiedades) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-1 border-b border-slate-100 pb-4 dark:border-[#1e2c44]">
      <h3 className="text-base font-semibold text-slate-900 dark:text-white">{titulo}</h3>
      <p className="text-xs text-slate-500 dark:text-slate-400">
        {total === 1 ? "1 en total" : `${total} en total`}
        {paginas > 1 ? ` · ${paginas} páginas` : ""}
      </p>
    </div>
  );
}
