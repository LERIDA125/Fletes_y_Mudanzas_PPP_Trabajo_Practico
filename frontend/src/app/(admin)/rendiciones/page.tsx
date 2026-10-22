"use client";

import {
  CheckCircle2,
  CircleDollarSign,
  Download,
  Filter,
  MoreHorizontal,
  Plus,
  ReceiptText,
  Search,
  WalletCards,
} from "lucide-react";
import { useState } from "react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const liquidaciones = [
  {
    chofer: "Lucas Ramírez",
    dni: "38.291.442",
    iniciales: "LR",
    viajes: 2,
    efectivo: 45000,
    transferencias: 55000,
    total: 100000,
    rendido: 100000,
    diferencia: 0,
    estado: "Rendido",
    badgeClase: "border-emerald-200 bg-emerald-50 text-emerald-700",
  },
  {
    chofer: "Sofía Martínez",
    dni: "40.119.823",
    iniciales: "SM",
    viajes: 1,
    efectivo: 35000,
    transferencias: 0,
    total: 35000,
    rendido: 0,
    diferencia: 35000,
    estado: "Pendiente",
    badgeClase: "border-amber-200 bg-amber-50 text-amber-700",
  },
  {
    chofer: "Diego Acosta",
    dni: "35.882.109",
    iniciales: "DA",
    viajes: 2,
    efectivo: 50000,
    transferencias: 95000,
    total: 145000,
    rendido: 0,
    diferencia: 145000,
    estado: "En viaje",
    badgeClase: "border-sky-200 bg-sky-50 text-sky-700",
  },
  {
    chofer: "Martín Soto",
    dni: "33.742.610",
    iniciales: "MS",
    viajes: 2,
    efectivo: 20000,
    transferencias: 80000,
    total: 100000,
    rendido: 100000,
    diferencia: 0,
    estado: "Rendido",
    badgeClase: "border-emerald-200 bg-emerald-50 text-emerald-700",
  },
];

const formatoMoneda = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
  maximumFractionDigits: 0,
});

export default function PaginaRendiciones() {
  const [criterio, setCriterio] = useState("");

  const filtrados = liquidaciones.filter((l) =>
    l.chofer.toLowerCase().includes(criterio.toLowerCase()),
  );

  return (
    <div className="flex flex-col gap-7">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-sm font-medium text-orange-600">
            Control de caja y liquidaciones
          </p>
          <h2 className="text-2xl font-bold tracking-tight sm:text-3xl text-slate-950">
            Rendiciones y Cobranzas
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Seguimiento de dinero recaudado por choferes y arqueo de caja diario.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" className="gap-1.5">
            <Download className="size-4 text-slate-600" />
            <span className="hidden sm:inline">Exportar reporte</span>
          </Button>
          <Button className="bg-orange-500 shadow-sm shadow-orange-200 hover:bg-orange-600 text-white font-medium">
            <Plus className="size-4" />
            Nueva rendición
          </Button>
        </div>
      </div>

      {/* Tarjetas KPI económicas */}
      <section
        className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
        aria-label="Indicadores económicos"
      >
        <Card className="border-slate-200 shadow-none">
          <CardContent className="p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">Recaudación del día</p>
                <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
                  {formatoMoneda.format(380000)}
                </p>
              </div>
              <div className="flex size-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                <CircleDollarSign className="size-5" />
              </div>
            </div>
            <p className="mt-4 flex items-center gap-1 text-xs text-slate-500">
              <span className="font-semibold text-emerald-600">7 servicios</span>{" "}
              liquidados
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-none">
          <CardContent className="p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">Efectivo en choferes</p>
                <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
                  {formatoMoneda.format(150000)}
                </p>
              </div>
              <div className="flex size-10 items-center justify-center rounded-xl bg-orange-50 text-orange-600">
                <WalletCards className="size-5" />
              </div>
            </div>
            <p className="mt-4 flex items-center gap-1 text-xs text-slate-500">
              <span className="font-semibold text-amber-600">2 choferes</span> con cobros
              en mano
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-none">
          <CardContent className="p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">Transferencias / Bancos</p>
                <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
                  {formatoMoneda.format(230000)}
                </p>
              </div>
              <div className="flex size-10 items-center justify-center rounded-xl bg-sky-50 text-sky-600">
                <ReceiptText className="size-5" />
              </div>
            </div>
            <p className="mt-4 flex items-center gap-1 text-xs text-slate-500">
              <span className="font-semibold text-sky-600">Acreditado</span> en cuenta
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-none">
          <CardContent className="p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">Diferencias de caja</p>
                <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
                  $0
                </p>
              </div>
              <div className="flex size-10 items-center justify-center rounded-xl bg-violet-50 text-violet-600">
                <CheckCircle2 className="size-5" />
              </div>
            </div>
            <p className="mt-4 flex items-center gap-1 text-xs text-slate-500">
              <span className="font-semibold text-emerald-600">Arqueo exacto</span> sin
              faltantes
            </p>
          </CardContent>
        </Card>
      </section>

      {/* Tabla principal de liquidaciones */}
      <Card className="border-slate-200 shadow-none overflow-hidden">
        <CardHeader className="flex flex-col gap-4 border-b border-slate-100 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle className="text-base font-semibold text-slate-900">
              Rendiciones por chofer
            </CardTitle>
            <p className="mt-1 text-sm text-slate-500">
              Arqueo de cobros del día lunes, 24 de junio de 2024.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative flex items-center">
              <Search className="pointer-events-none absolute left-3 size-4 text-slate-400" />
              <input
                type="search"
                value={criterio}
                onChange={(e) => setCriterio(e.target.value)}
                placeholder="Buscar chofer…"
                className="w-full sm:w-60 rounded-lg border border-slate-200 bg-white pl-9 pr-3 py-1.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-950 focus:outline-none focus:ring-1 focus:ring-slate-950"
              />
            </div>
            <Button variant="outline" size="sm" className="gap-1.5">
              <Filter className="size-3.5 text-slate-500" />
              <span>Estado</span>
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50/70 hover:bg-slate-50/70">
                  <TableHead className="pl-5 sm:pl-6">Chofer</TableHead>
                  <TableHead className="text-center">Viajes</TableHead>
                  <TableHead className="text-right">Efectivo cobrado</TableHead>
                  <TableHead className="text-right">Transferencias</TableHead>
                  <TableHead className="text-right">Total a rendir</TableHead>
                  <TableHead className="text-right">Rendido</TableHead>
                  <TableHead className="text-center">Estado</TableHead>
                  <TableHead className="pr-5 sm:pr-6 text-right">
                    <span className="sr-only">Acciones</span>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtrados.map((item) => (
                  <TableRow key={item.chofer} className="text-sm">
                    <TableCell className="whitespace-nowrap pl-5 sm:pl-6 font-medium text-slate-900">
                      <div className="flex items-center gap-3">
                        <Avatar className="size-8">
                          <AvatarFallback className="bg-slate-100 text-xs font-semibold text-slate-700">
                            {item.iniciales}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-semibold text-slate-900">{item.chofer}</p>
                          <p className="text-xs text-slate-500 font-normal">
                            DNI {item.dni}
                          </p>
                        </div>
                      </div>
                    </TableCell>

                    <TableCell className="text-center whitespace-nowrap">
                      <span className="inline-flex items-center rounded-md bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-700">
                        {item.viajes} viajes
                      </span>
                    </TableCell>

                    <TableCell className="whitespace-nowrap text-right tabular-nums text-slate-700">
                      {formatoMoneda.format(item.efectivo)}
                    </TableCell>

                    <TableCell className="whitespace-nowrap text-right tabular-nums text-slate-700">
                      {formatoMoneda.format(item.transferencias)}
                    </TableCell>

                    <TableCell className="whitespace-nowrap text-right font-bold text-slate-950 tabular-nums">
                      {formatoMoneda.format(item.total)}
                    </TableCell>

                    <TableCell className="whitespace-nowrap text-right font-semibold text-emerald-600 tabular-nums">
                      {formatoMoneda.format(item.rendido)}
                    </TableCell>

                    <TableCell className="text-center whitespace-nowrap">
                      <Badge variant="outline" className={item.badgeClase}>
                        {item.estado}
                      </Badge>
                    </TableCell>

                    <TableCell className="pr-5 text-right sm:pr-6 whitespace-nowrap">
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Opciones de ${item.chofer}`}
                      >
                        <MoreHorizontal className="size-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <div className="flex items-center justify-between border-t border-slate-100 px-5 py-4 text-xs text-slate-500 sm:px-6">
            <span>Mostrando {filtrados.length} liquidaciones</span>
            <span className="font-medium text-slate-700">
              Total efectivo auditado: {formatoMoneda.format(150000)}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
