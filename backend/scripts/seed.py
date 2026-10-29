import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.models.chofer import ChoferORM
from app.infrastructure.models.cliente import ClienteORM
from app.infrastructure.models.servicio import ServicioORM
from app.infrastructure.models.tipo_vehiculo import TipoVehiculoORM
from app.infrastructure.models.vehiculo import VehiculoORM


def _normalizar_texto(texto: str) -> str:
    import unicodedata

    texto_normalizado = unicodedata.normalize("NFKD", texto)
    sin_acentos = "".join(c for c in texto_normalizado if not unicodedata.combining(c))
    return " ".join(sin_acentos.lower().split())


def run_seed():
    db = SessionLocal()
    try:
        db.query(ServicioORM).delete()
        db.query(VehiculoORM).delete()
        db.query(TipoVehiculoORM).delete()
        db.query(ChoferORM).delete()
        db.query(ClienteORM).delete()
        db.commit()

        tipos_data = [
            ("Furgón Grande", Decimal("25000.00"), Decimal("850.00")),
            ("Camioneta Mediana", Decimal("18000.00"), Decimal("650.00")),
            ("Furgón Chico", Decimal("15000.00"), Decimal("550.00")),
        ]
        db_tipos = []
        for desc, tarifa_hora, tarifa_km in tipos_data:
            tipo = TipoVehiculoORM(
                descripcion=desc,
                descripcion_key=_normalizar_texto(desc),
                capacidad_carga_kg=Decimal("1000.00"),
                tarifa_hora_base=tarifa_hora,
                tarifa_km_excedente=tarifa_km,
                activo=True,
            )
            db_tipos.append(tipo)
        db.add_all(db_tipos)
        db.commit()
        for t in db_tipos:
            db.refresh(t)

        nombres = [
            "Marcelo Rodriguez",
            "El Ruso",
            "Cacho Benitez",
            "Hernan Perez",
            "Sergio Gomez",
            "Daniel Silva",
            "Jorge Medina",
            "Carlos Garcia",
            "Matias Fernandez",
            "Lucas Ramirez",
        ]
        db_choferes = [
            ChoferORM(
                nombre_completo=n,
                telefono=f"11-{random.randint(2000, 7999)}-{random.randint(1000, 9999)}",
                activo=True,
            )
            for n in nombres
        ]
        db.add_all(db_choferes)
        db.commit()
        for c in db_choferes:
            db.refresh(c)

        db_vehiculos = []
        for i in range(5):
            vehiculo = VehiculoORM(
                patente=f"ABC{random.randint(100, 999)}",
                id_tipo_vehiculo=db_tipos[i % 3].id,
                id_chofer_habitual=db_choferes[i].id,
                activo=True,
            )
            db.add(vehiculo)
            db_vehiculos.append(vehiculo)
        db.commit()
        for v in db_vehiculos:
            db.refresh(v)

        nombres_clientes = [
            "Muebles Belgrano S.R.L.",
            "Lucia Mendez",
            "Estudio Jurídico Perez & Asoc",
            "Gimnasio Iron",
            "Juan Carlos Gomez",
            "Librería Ateneo",
            "Mecánica Los Hermanos",
            "Verdulería Don José",
            "Ferretería El Tuerca",
            "Bazar Oriental",
            "Carlos Tevez",
            "Panadería La Espiga",
            "Farmacia Pasteur",
            "Constructora Cimientos",
            "Supermercado Día",
            "Gráfica Impresiones",
            "Carnicería La Vaquita",
            "Rucci Fernando SRL",
            "Kiosco El Paso",
            "Pinturerías Colorin",
        ]
        db_clientes = []
        for n in nombres_clientes:
            db_clientes.append(
                ClienteORM(
                    razon_social=n,
                    razon_social_key=_normalizar_texto(n),
                    telefono=f"11-{random.randint(4000, 6999)}-1111",
                    direccion_habitual="Capital Federal",
                    tiene_cuenta_corriente=False,
                    activo=True,
                    creado_en=datetime.now(),
                    actualizado_en=datetime.now(),
                )
            )
        db.add_all(db_clientes)
        db.commit()
        for c in db_clientes:
            db.refresh(c)

        hoy = date.today()
        fechas = (
            [hoy - timedelta(days=1)] * 3
            + [hoy] * 5
            + [hoy + timedelta(days=i) for i in range(1, 8)]
        )
        horas = [time(8, 0), time(9, 30), time(11, 0), time(14, 0), time(16, 30)]

        for i in range(15):
            cliente = random.choice(db_clientes)
            fecha_serv = fechas[i]

            if i % 3 == 0:
                chofer_id = None
                vehiculo_id = None
                tipo_id = random.choice(db_tipos).id
                estado = "pendiente"
            else:
                vehiculo = random.choice(db_vehiculos)
                chofer_id = vehiculo.id_chofer_habitual
                vehiculo_id = vehiculo.id
                tipo_id = vehiculo.id_tipo_vehiculo
                if fecha_serv > hoy:
                    estado = "confirmado"
                elif fecha_serv < hoy:
                    estado = "finalizado"
                else:
                    estado = random.choice(["en curso", "finalizado"])

            servicio = ServicioORM(
                id_cliente=cliente.id,
                id_tipo_vehiculo=tipo_id,
                fecha=fecha_serv,
                hora_inicio=random.choice(horas),
                estado=estado,
                id_chofer=chofer_id,
                id_vehiculo=vehiculo_id,
                horas_estimadas=Decimal("2.50"),
                distancia_ida_km=Decimal("15.00"),
                distancia_total_km=Decimal("30.00"),
                km_franquicia=Decimal("10.00"),
                km_excedente=Decimal("20.00"),
                tarifa_hora_aplicada=Decimal("12500.00"),
                tarifa_km_aplicada=Decimal("450.00"),
                precio_total=Decimal("40250.00"),
            )
            db.add(servicio)

        db.commit()
        print("¡Base poblada con éxito!")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
