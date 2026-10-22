"use client";

import {
  ArrowUpRight,
  CarFront,
  CircleDollarSign,
  ClipboardList,
  MoreHorizontal,
  Plus,
  Search,
  UserRound,
  WalletCards,
} from "lucide-react";
import Link from "next/link";

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

const services = [
  {
    time: "08:30",
    client: "María González",
    origin: "Palermo, CABA",
    destination: "Nordelta, Tigre",
    driver: "Lucas Ramírez",
    initials: "LR",
    vehicle: "Grande",
    status: "En curso",
  },
  {
    time: "10:00",
    client: "Estudio Norte",
    origin: "Belgrano, CABA",
    destination: "Vicente López",
    driver: "Sofía Martínez",
    initials: "SM",
    vehicle: "Chico",
    status: "Pendiente",
  },
  {
    time: "11:30",
    client: "Tomás Fernández",
    origin: "San Isidro",
    destination: "Pilar",
    driver: "Diego Acosta",
    initials: "DA",
    vehicle: "Grande",
    status: "Pendiente",
  },
  {
    time: "14:00",
    client: "Casa Clara Deco",
    origin: "Villa Crespo",
    destination: "Recoleta, CABA",
    driver: "—",
    initials: "—",
    vehicle: "Chico",
    status: "Pendiente",
  },
  {
    time: "16:30",
    client: "Valentina Ruiz",
    origin: "Caballito, CABA",
    destination: "Haedo, Morón",
    driver: "Martín Soto",
    initials: "MS",
    vehicle: "Grande",
    status: "Finalizado",
  },
];

const statusStyles = {
  "En curso": "border-sky-200 bg-sky-50 text-sky-700",
  Pendiente: "border-amber-200 bg-amber-50 text-amber-700",
  Finalizado: "border-emerald-200 bg-emerald-50 text-emerald-700",
};

export default function Page() {
  return (
    <div className="flex flex-col gap-7">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="mb-1 text-sm font-medium text-orange-600">Resumen operativo</p>
          <h2 className="text-2xl font-bold tracking-tight sm:text-3xl text-slate-950">
            Dashboard
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Este es el estado de tu operación para hoy.
          </p>
        </div>
        <Link href="/servicios">
          <Button className="hidden bg-orange-500 shadow-sm shadow-orange-200 hover:bg-orange-600 sm:flex text-white font-medium">
            <Plus className="size-4" />
            Nuevo Servicio / Cotizar
          </Button>
        </Link>
      </div>

      <section
        className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
        aria-label="Indicadores clave"
      >
        {[
          {
            label: "Servicios del día",
            value: "8",
            change: "+12,5%",
            note: "vs. semana pasada",
            icon: ClipboardList,
            tone: "bg-orange-50 text-orange-600",
          },
          {
            label: "Choferes disponibles",
            value: "3",
            change: "de 12",
            note: "en la flota activa",
            icon: UserRound,
            tone: "bg-sky-50 text-sky-600",
          },
          {
            label: "Dinero por cobrar hoy",
            value: "$150.000",
            change: "+8,2%",
            note: "vs. ayer",
            icon: CircleDollarSign,
            tone: "bg-emerald-50 text-emerald-600",
          },
          {
            label: "Pendiente de rendición",
            value: "$50.000",
            change: "2 servicios",
            note: "requieren revisión",
            icon: WalletCards,
            tone: "bg-violet-50 text-violet-600",
          },
        ].map((kpi) => {
          const Icon = kpi.icon;
          return (
            <Card key={kpi.label} className="border-slate-200 shadow-none">
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm text-slate-500">{kpi.label}</p>
                    <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
                      {kpi.value}
                    </p>
                  </div>
                  <div
                    className={`flex size-10 items-center justify-center rounded-xl ${kpi.tone}`}
                  >
                    <Icon className="size-5" />
                  </div>
                </div>
                <p className="mt-4 flex items-center gap-1 text-xs text-slate-500">
                  <span className="font-semibold text-emerald-600">{kpi.change}</span>
                  {kpi.note}
                </p>
              </CardContent>
            </Card>
          );
        })}
      </section>

      <Card className="border-slate-200 shadow-none">
        <CardHeader className="flex flex-row items-center justify-between gap-4 border-b border-slate-100 px-5 py-5 sm:px-6">
          <div>
            <CardTitle className="text-base font-semibold text-slate-900">
              Próximos Servicios
            </CardTitle>
            <p className="mt-1 text-sm text-slate-500">
              Servicios programados para hoy, 24 de junio
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" className="hidden sm:flex">
              <Search className="size-3.5" />
              Buscar
            </Button>
            <Button variant="ghost" size="icon" aria-label="Más opciones">
              <MoreHorizontal className="size-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50/70 hover:bg-slate-50/70">
                  <TableHead className="pl-5 sm:pl-6">Horario</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Origen</TableHead>
                  <TableHead>Destino</TableHead>
                  <TableHead>Chofer asignado</TableHead>
                  <TableHead>Vehículo</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="pr-5 sm:pr-6" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {services.map((service) => (
                  <TableRow key={`${service.time}-${service.client}`} className="text-sm">
                    <TableCell className="whitespace-nowrap pl-5 font-semibold text-slate-900 sm:pl-6">
                      {service.time}
                    </TableCell>
                    <TableCell className="whitespace-nowrap font-medium text-slate-900">
                      {service.client}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-slate-500">
                      {service.origin}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-slate-500">
                      {service.destination}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2 whitespace-nowrap">
                        {service.initials === "—" ? (
                          <div className="flex size-7 items-center justify-center rounded-full border border-dashed border-slate-300 text-xs text-slate-400">
                            —
                          </div>
                        ) : (
                          <Avatar className="size-7">
                            <AvatarFallback className="bg-slate-100 text-[10px] font-semibold text-slate-600">
                              {service.initials}
                            </AvatarFallback>
                          </Avatar>
                        )}
                        <span
                          className={
                            service.driver === "—" ? "text-slate-400" : "text-slate-800"
                          }
                        >
                          {service.driver}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="inline-flex items-center gap-1.5 text-slate-600">
                        <CarFront className="size-4 text-slate-400" />
                        {service.vehicle}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={
                          statusStyles[service.status as keyof typeof statusStyles]
                        }
                      >
                        {service.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="pr-5 text-right sm:pr-6">
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Opciones de ${service.client}`}
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
            <span>Mostrando 5 de 8 servicios</span>
            <Link
              href="/servicios"
              className="inline-flex items-center gap-1 text-slate-700 hover:text-slate-950 font-medium"
            >
              <span>Ver agenda completa</span>
              <ArrowUpRight className="size-3.5" />
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
