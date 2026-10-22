"use client";

import {
  CalendarDays,
  CarFront,
  ChevronLeft,
  ChevronRight,
  Clock,
  Filter,
  MoreHorizontal,
  Plus,
  Truck,
  UserRound,
} from "lucide-react";
import { useState } from "react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const turnos = [
  {
    hora: "08:30",
    cliente: "María González",
    origen: "Palermo, CABA",
    destino: "Nordelta, Tigre",
    chofer: "Lucas Ramírez",
    iniciales: "LR",
    vehiculo: "Furgón Grande (AF-123-JK)",
    estado: "En curso",
    estadoBadge: "border-sky-200 bg-sky-50 text-sky-700",
    duracion: "2h 30m",
  },
  {
    hora: "10:00",
    cliente: "Estudio Norte",
    origen: "Belgrano, CABA",
    destino: "Vicente López",
    chofer: "Sofía Martínez",
    iniciales: "SM",
    vehiculo: "Camioneta Chica (AE-982-PL)",
    estado: "Pendiente",
    estadoBadge: "border-amber-200 bg-amber-50 text-amber-700",
    duracion: "1h 45m",
  },
  {
    hora: "11:30",
    cliente: "Tomás Fernández",
    origen: "San Isidro",
    destino: "Pilar",
    chofer: "Diego Acosta",
    iniciales: "DA",
    vehiculo: "Furgón Grande (AG-441-TR)",
    estado: "Pendiente",
    estadoBadge: "border-amber-200 bg-amber-50 text-amber-700",
    duracion: "3h 00m",
  },
  {
    hora: "14:00",
    cliente: "Casa Clara Deco",
    origen: "Villa Crespo",
    destino: "Recoleta, CABA",
    chofer: "Sin chofer asignado",
    iniciales: "—",
    vehiculo: "Camioneta Chica",
    estado: "Pendiente",
    estadoBadge: "border-amber-200 bg-amber-50 text-amber-700",
    duracion: "2h 00m",
  },
  {
    hora: "16:30",
    cliente: "Valentina Ruiz",
    origen: "Caballito, CABA",
    destino: "Haedo, Morón",
    chofer: "Martín Soto",
    iniciales: "MS",
    vehiculo: "Furgón Grande (AD-552-ZX)",
    estado: "Finalizado",
    estadoBadge: "border-emerald-200 bg-emerald-50 text-emerald-700",
    duracion: "2h 15m",
  },
];

const choferesDisponibilidad = [
  { nombre: "Lucas Ramírez", estado: "En ruta", estadoColor: "bg-sky-500" },
  { nombre: "Sofía Martínez", estado: "Asignada", estadoColor: "bg-amber-500" },
  { nombre: "Diego Acosta", estado: "Asignado", estadoColor: "bg-amber-500" },
  { nombre: "Martín Soto", estado: "Disponible", estadoColor: "bg-emerald-500" },
  { nombre: "Esteban Quiroga", estado: "Disponible", estadoColor: "bg-emerald-500" },
  { nombre: "Julián Varela", estado: "Franco", estadoColor: "bg-slate-400" },
];

export default function PaginaAgenda() {
  const [vista, setVista] = useState<"dia" | "semana">("dia");

  return (
    <div className="flex flex-col gap-7">
      {/* Encabezado */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-sm font-medium text-orange-600">
            Planificación operativa
          </p>
          <h2 className="text-2xl font-bold tracking-tight sm:text-3xl text-slate-950">
            Agenda de Servicios
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Cronograma de viajes, franjas horarias y disponibilidad de choferes.
          </p>
        </div>

        <Button className="bg-orange-500 shadow-sm shadow-orange-200 hover:bg-orange-600 text-white font-medium self-start sm:self-auto">
          <Plus className="size-4" />
          Programar viaje
        </Button>
      </div>

      {/* Tarjetas KPI de disponibilidad */}
      <section
        className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
        aria-label="Disponibilidad del día"
      >
        <Card className="border-slate-200 shadow-none">
          <CardContent className="p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">Viajes programados</p>
                <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
                  5 viajes
                </p>
              </div>
              <div className="flex size-10 items-center justify-center rounded-xl bg-orange-50 text-orange-600">
                <CalendarDays className="size-5" />
              </div>
            </div>
            <p className="mt-4 flex items-center gap-1 text-xs text-slate-500">
              <span className="font-semibold text-emerald-600">100%</span> turnos
              cubiertos
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-none">
          <CardContent className="p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">Choferes en ruta</p>
                <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
                  1 activo
                </p>
              </div>
              <div className="flex size-10 items-center justify-center rounded-xl bg-sky-50 text-sky-600">
                <UserRound className="size-5" />
              </div>
            </div>
            <p className="mt-4 flex items-center gap-1 text-xs text-slate-500">
              <span className="font-semibold text-slate-700">2 asignados</span> para hoy
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-none">
          <CardContent className="p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">Vehículos en uso</p>
                <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
                  3 unidades
                </p>
              </div>
              <div className="flex size-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                <Truck className="size-5" />
              </div>
            </div>
            <p className="mt-4 flex items-center gap-1 text-xs text-slate-500">
              <span className="font-semibold text-emerald-600">5 disponibles</span> en
              base
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-none">
          <CardContent className="p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">Franjas libres hoy</p>
                <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
                  4 turnos
                </p>
              </div>
              <div className="flex size-10 items-center justify-center rounded-xl bg-violet-50 text-violet-600">
                <Clock className="size-5" />
              </div>
            </div>
            <p className="mt-4 flex items-center gap-1 text-xs text-slate-500">
              <span className="font-semibold text-violet-600">Turno tarde</span> con
              capacidad
            </p>
          </CardContent>
        </Card>
      </section>

      {/* Barra de navegación de fecha y selector de vista */}
      <div className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-none sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center rounded-lg border border-slate-200 bg-white">
            <Button
              variant="ghost"
              size="icon"
              className="size-8"
              aria-label="Día anterior"
            >
              <ChevronLeft className="size-4" />
            </Button>
            <span className="px-3 text-sm font-semibold text-slate-900">
              Lunes, 24 de junio de 2024
            </span>
            <Button
              variant="ghost"
              size="icon"
              className="size-8"
              aria-label="Día siguiente"
            >
              <ChevronRight className="size-4" />
            </Button>
          </div>
          <Button variant="outline" size="sm" className="hidden sm:inline-flex">
            Hoy
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-slate-200 bg-slate-50 p-1">
            <button
              type="button"
              onClick={() => setVista("dia")}
              className={`rounded-md px-3 py-1 text-xs font-semibold transition-colors ${
                vista === "dia"
                  ? "bg-white text-slate-950 shadow-xs"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              Vista Día
            </button>
            <button
              type="button"
              onClick={() => setVista("semana")}
              className={`rounded-md px-3 py-1 text-xs font-semibold transition-colors ${
                vista === "semana"
                  ? "bg-white text-slate-950 shadow-xs"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              Vista Semana
            </button>
          </div>

          <Button variant="outline" size="sm" className="gap-1.5">
            <Filter className="size-3.5 text-slate-500" />
            <span>Filtrar</span>
          </Button>
        </div>
      </div>

      {/* Grilla principal con turnos y panel lateral de disponibilidad */}
      <div className="grid gap-7 lg:grid-cols-3">
        {/* Cronograma de turnos del día */}
        <div className="flex flex-col gap-4 lg:col-span-2">
          <Card className="border-slate-200 shadow-none">
            <CardHeader className="border-b border-slate-100 px-5 py-4">
              <CardTitle className="text-base font-semibold text-slate-900">
                Turnos programados
              </CardTitle>
            </CardHeader>
            <CardContent className="divide-y divide-slate-100 p-0">
              {turnos.map((t) => (
                <div
                  key={`${t.hora}-${t.cliente}`}
                  className="flex flex-col gap-3 p-5 transition-colors hover:bg-slate-50/70 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex flex-col items-center justify-center rounded-lg bg-slate-100 px-3 py-2 text-center">
                      <span className="text-sm font-bold text-slate-900">{t.hora}</span>
                      <span className="text-[10px] text-slate-500 font-medium">
                        {t.duracion}
                      </span>
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-semibold text-slate-900">{t.cliente}</h4>
                        <Badge variant="outline" className={t.estadoBadge}>
                          {t.estado}
                        </Badge>
                      </div>
                      <p className="mt-1 text-xs text-slate-500">
                        {t.origen} → <span className="font-medium">{t.destino}</span>
                      </p>
                      <p className="mt-1 flex items-center gap-1.5 text-xs text-slate-600">
                        <CarFront className="size-3.5 text-slate-400" />
                        <span>{t.vehiculo}</span>
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between gap-3 sm:justify-end">
                    <div className="flex items-center gap-2">
                      {t.iniciales === "—" ? (
                        <div className="flex size-7 items-center justify-center rounded-full border border-dashed border-slate-300 text-xs text-slate-400">
                          —
                        </div>
                      ) : (
                        <Avatar className="size-7">
                          <AvatarFallback className="bg-slate-100 text-[10px] font-semibold text-slate-600">
                            {t.iniciales}
                          </AvatarFallback>
                        </Avatar>
                      )}
                      <span
                        className={`text-xs font-medium ${
                          t.chofer === "Sin chofer asignado"
                            ? "text-slate-400 italic"
                            : "text-slate-800"
                        }`}
                      >
                        {t.chofer}
                      </span>
                    </div>

                    <Button variant="ghost" size="icon" aria-label="Opciones de turno">
                      <MoreHorizontal className="size-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Panel lateral: Estado de choferes */}
        <div className="flex flex-col gap-4">
          <Card className="border-slate-200 shadow-none">
            <CardHeader className="border-b border-slate-100 px-5 py-4">
              <CardTitle className="text-base font-semibold text-slate-900">
                Choferes en servicio
              </CardTitle>
            </CardHeader>
            <CardContent className="divide-y divide-slate-100 p-0">
              {choferesDisponibilidad.map((c) => (
                <div
                  key={c.nombre}
                  className="flex items-center justify-between px-5 py-3.5 text-sm"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex size-8 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-700">
                      {c.nombre
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </div>
                    <span className="font-medium text-slate-900">{c.nombre}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`size-2 rounded-full ${c.estadoColor}`}
                      aria-hidden="true"
                    />
                    <span className="text-xs text-slate-600 font-medium">{c.estado}</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
