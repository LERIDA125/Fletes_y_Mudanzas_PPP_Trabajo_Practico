type Propiedades = {
  total: number;
  paginas: number;
};

export function CabeceraListado({ total, paginas }: Propiedades) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-1 border-b border-slate-100 pb-4">
      <h3 className="text-base font-semibold text-slate-900">Vehículos</h3>
      <p className="text-xs text-slate-500">
        {total === 1 ? "1 en total" : `${total} en total`}
        {paginas > 1 ? ` · ${paginas} páginas` : ""}
      </p>
    </div>
  );
}
