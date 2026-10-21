type Propiedades = {
  total: number;
  paginas: number;
};

export function CabeceraListado({ total, paginas }: Propiedades) {
  return (
    <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 px-4 sm:px-0">
      <h1 className="text-[1.5rem] font-semibold leading-tight text-tinta">Clientes</h1>
      <p className="text-[0.875rem] text-tinta-media">
        {total === 1 ? "1 en total" : `${total} en total`}
        {paginas > 1 ? ` · ${paginas} páginas` : ""}
      </p>
    </div>
  );
}
