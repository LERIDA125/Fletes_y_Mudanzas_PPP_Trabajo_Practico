'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  ArrowRight,
  CalendarDays,
  Check,
  ChevronRight,
  CircleDollarSign,
  Clock3,
  LogOut,
  MapPin,
  MessageCircle,
  Navigation,
  Package,
  Phone,
  Receipt,
  Truck,
  UserRound,
  WalletCards,
} from 'lucide-react'

type TripStatus = 'pending' | 'en-route' | 'completed'

type Trip = {
  id: number
  time: string
  period: string
  client: string
  phone: string
  origin: string
  destination: string
  packages: string
  notes: string
  amount?: string
  status: TripStatus
}

const initialTrips: Trip[] = [
  {
    id: 1,
    time: '08:30',
    period: 'AM',
    client: 'María González',
    phone: '+54 9 11 4567 8901',
    origin: 'Av. Cabildo 1840, Belgrano',
    destination: 'Aráoz 320, Palermo',
    packages: '12 bultos',
    notes: 'Llevar cuerdas y mantas',
    amount: '$ 18.500',
    status: 'pending',
  },
  {
    id: 2,
    time: '11:15',
    period: 'AM',
    client: 'Estudio Pampa',
    phone: '+54 9 11 3188 2400',
    origin: 'Lima 760, San Telmo',
    destination: 'Av. Libertador 6420, Núñez',
    packages: '8 bultos',
    notes: 'Fragil · Cargar por ascensor',
    status: 'en-route',
  },
  {
    id: 3,
    time: '15:45',
    period: 'PM',
    client: 'Tomás Ruiz',
    phone: '+54 9 11 6012 7799',
    origin: 'Juncal 2240, Recoleta',
    destination: 'Mendoza 4900, Villa Urquiza',
    packages: '5 bultos',
    notes: 'Avisar 15 min antes de llegar',
    amount: '$ 12.000',
    status: 'pending',
  },
]

const statusCopy: Record<TripStatus, { label: string; button: string }> = {
  pending: { label: 'Pendiente', button: 'Marcar como En Camino' },
  'en-route': { label: 'En camino', button: 'Finalizar Viaje y Rendir' },
  completed: { label: 'Completado', button: 'Viaje finalizado' },
}

export default function Page() {
  const [trips, setTrips] = useState(initialTrips)
  const [activeTab, setActiveTab] = useState('Viajes de hoy')

  function advanceTrip(id: number) {
    setTrips((current) =>
      current.map((trip) =>
        trip.id === id
          ? { ...trip, status: trip.status === 'pending' ? 'en-route' : 'completed' }
          : trip,
      ),
    )
  }

  return (
    <main className="min-h-screen bg-[#dce9e5] px-0 py-0 text-[#173b38] sm:flex sm:items-center sm:justify-center sm:p-8">
      <div className="relative mx-auto flex min-h-screen w-full max-w-[430px] flex-col overflow-hidden bg-[#f5f8f7] shadow-2xl sm:min-h-[850px] sm:max-h-[900px] sm:rounded-[2.5rem] sm:border-[8px] sm:border-[#173b38]">
        <header className="bg-[#173b38] px-5 pb-6 pt-7 text-white">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-[13px] font-medium text-[#b4d6cc]">Martes 24 de junio, 2025</p>
              <h1 className="mt-1 text-[27px] font-bold tracking-[-0.03em]">Hola, Carlos</h1>
            </div>
            <Button aria-label="Cerrar sesión" className="mt-0.5 size-10 rounded-xl bg-white/10 text-white hover:bg-white/20" size="icon">
              <LogOut aria-hidden="true" />
            </Button>
          </div>
          <div className="mt-5 flex items-center gap-2 text-sm text-[#d8ebe5]">
            <span className="flex size-7 items-center justify-center rounded-full bg-[#efb366] text-[#173b38]"><Truck aria-hidden="true" className="size-4" /></span>
            <span>Tu jornada está en marcha</span>
          </div>
        </header>

        <section className="flex-1 overflow-y-auto px-4 pb-28 pt-6">
          <div className="mb-5 flex items-end justify-between px-1">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-[#78918b]">Agenda del día</p>
              <h2 className="mt-1 text-[22px] font-bold tracking-[-0.03em]">Tus viajes de hoy</h2>
            </div>
            <span className="rounded-full bg-[#d9eee6] px-3 py-1 text-xs font-bold text-[#28765f]">{trips.length} viajes</span>
          </div>

          <div className="flex flex-col gap-4">
            {trips.map((trip) => {
              const completed = trip.status === 'completed'
              const active = trip.status === 'en-route'
              return (
                <article key={trip.id} className="overflow-hidden rounded-[22px] border border-[#dce8e4] bg-white shadow-[0_5px_18px_rgba(31,78,68,0.07)]">
                  <div className="flex items-center justify-between border-b border-[#edf2f0] px-4 py-3.5">
                    <div className="flex items-center gap-3">
                      <div className="flex items-baseline gap-1.5 rounded-xl bg-[#eef6f3] px-3 py-2 text-[#216954]">
                        <Clock3 aria-hidden="true" className="mr-0.5 size-4 self-center" />
                        <span className="text-xl font-bold leading-none">{trip.time}</span>
                        <span className="text-[10px] font-bold uppercase">{trip.period}</span>
                      </div>
                      <span className={`rounded-full px-2.5 py-1 text-[11px] font-bold ${completed ? 'bg-[#e8f0ed] text-[#718782]' : active ? 'bg-[#fff0d7] text-[#a66a16]' : 'bg-[#e6f5ee] text-[#297459]'}`}>
                        {statusCopy[trip.status].label}
                      </span>
                    </div>
                    <span className="text-xs font-bold text-[#9aada8]">#{String(trip.id).padStart(2, '0')}</span>
                  </div>

                  <div className="flex flex-col gap-4 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex min-w-0 items-center gap-3">
                        <div className="flex size-10 shrink-0 items-center justify-center rounded-full bg-[#f4e8d9] text-[#a76a24]"><UserRound aria-hidden="true" className="size-[18px]" /></div>
                        <div className="min-w-0">
                          <h3 className="truncate text-[15px] font-bold">{trip.client}</h3>
                          <p className="mt-0.5 text-xs text-[#738983]">{trip.phone}</p>
                        </div>
                      </div>
                      <div className="flex gap-1.5">
                        <a aria-label={`Llamar a ${trip.client}`} href={`tel:${trip.phone}`} className="flex size-9 items-center justify-center rounded-xl bg-[#edf6f3] text-[#28765f] transition-colors hover:bg-[#d9eee6]"><Phone aria-hidden="true" className="size-4" /></a>
                        <a aria-label={`Enviar WhatsApp a ${trip.client}`} href={`https://wa.me/${trip.phone.replace(/\D/g, '')}`} className="flex size-9 items-center justify-center rounded-xl bg-[#edf6f3] text-[#28765f] transition-colors hover:bg-[#d9eee6]"><MessageCircle aria-hidden="true" className="size-4" /></a>
                      </div>
                    </div>

                    <div className="relative flex flex-col gap-3 rounded-2xl bg-[#f7faf9] px-3.5 py-3">
                      <div className="absolute bottom-6 left-[21px] top-7 border-l border-dashed border-[#bad2ca]" />
                      <div className="relative flex gap-3"><span className="mt-0.5 flex size-[15px] shrink-0 items-center justify-center rounded-full border-[3px] border-[#4f9a7e] bg-white" /><div className="min-w-0"><p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#8da39d]">Origen</p><p className="truncate text-[13px] font-semibold">{trip.origin}</p></div></div>
                      <div className="relative flex gap-3"><MapPin aria-hidden="true" className="size-[15px] shrink-0 text-[#d67b52]" /><div className="min-w-0"><p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#8da39d]">Destino</p><p className="truncate text-[13px] font-semibold">{trip.destination}</p></div></div>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div className="rounded-xl bg-[#fffaf2] px-3 py-2.5"><div className="flex items-center gap-1.5 text-[#a97835]"><Package aria-hidden="true" className="size-3.5" /><span className="text-[10px] font-bold uppercase tracking-[0.08em]">Carga</span></div><p className="mt-1 text-xs font-bold">{trip.packages}</p></div>
                      <div className="rounded-xl bg-[#f7f8f8] px-3 py-2.5"><div className="flex items-center gap-1.5 text-[#78918b]"><Receipt aria-hidden="true" className="size-3.5" /><span className="text-[10px] font-bold uppercase tracking-[0.08em]">Notas</span></div><p className="mt-1 truncate text-xs font-bold">{trip.notes}</p></div>
                    </div>

                    {trip.amount && <div className="flex items-center justify-between rounded-xl border border-dashed border-[#edc988] bg-[#fff8e9] px-3.5 py-2.5"><div className="flex items-center gap-2 text-[#9e6b21]"><CircleDollarSign aria-hidden="true" className="size-4" /><span className="text-xs font-semibold">Cobrar en destino</span></div><strong className="text-sm text-[#8e5b14]">{trip.amount}</strong></div>}

                    <Button disabled={completed} onClick={() => advanceTrip(trip.id)} className={`h-12 w-full rounded-xl text-[13px] font-bold shadow-none ${completed ? 'bg-[#e9f0ed] text-[#78918b]' : active ? 'bg-[#d67b52] text-white hover:bg-[#c96f47]' : 'bg-[#28765f] text-white hover:bg-[#216550]'}`}>
                      {completed ? <Check data-icon="inline-start" /> : active ? <Receipt data-icon="inline-start" /> : <Navigation data-icon="inline-start" />}
                      {statusCopy[trip.status].button}
                      {!completed && <ChevronRight data-icon="inline-end" />}
                    </Button>
                  </div>
                </article>
              )
            })}
          </div>
        </section>

        <nav aria-label="Navegación principal" className="absolute inset-x-0 bottom-0 border-t border-[#deebe6] bg-white/95 px-5 pb-5 pt-3 backdrop-blur">
          <div className="flex items-center justify-around">
            {[
              { label: 'Agenda', icon: CalendarDays },
              { label: 'Viajes de hoy', icon: Truck },
              { label: 'Rendiciones', icon: WalletCards },
            ].map(({ label, icon: Icon }) => {
              const selected = activeTab === label
              return <button key={label} onClick={() => setActiveTab(label)} aria-current={selected ? 'page' : undefined} className={`flex min-w-[86px] flex-col items-center gap-1 rounded-xl px-2 py-1.5 text-[10px] font-bold transition-colors ${selected ? 'text-[#28765f]' : 'text-[#9baca8] hover:text-[#52756d]'}`}><span className={`flex size-8 items-center justify-center rounded-xl ${selected ? 'bg-[#e1f1eb]' : ''}`}><Icon aria-hidden="true" className="size-[18px]" /></span>{label}</button>
            })}
          </div>
        </nav>
      </div>
    </main>
  )
}
