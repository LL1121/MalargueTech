from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from inventario.models import Repuesto
from taller.models import Cliente, Equipo, OrdenReparacion, OrdenRepuesto
from usuarios.models import PerfilUsuario


class Command(BaseCommand):
    help = "Carga datos de demo para mostrar el sistema completo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Borra datos de demo existentes antes de volver a cargarlos.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get("reset"):
            self._reset_demo_data()

        owner, tech1, tech2 = self._seed_users()
        clientes = self._seed_clientes()
        equipos = self._seed_equipos(clientes)
        repuestos = self._seed_repuestos()
        self._seed_ordenes(equipos, repuestos, tech1, tech2)

        self.stdout.write(self.style.SUCCESS("Modo demo cargado correctamente ✅"))
        self.stdout.write("Usuarios demo:")
        self.stdout.write("- dueño: demo_owner / Demo1234!")
        self.stdout.write("- técnico 1: demo_tecnico1 / Demo1234!")
        self.stdout.write("- técnico 2: demo_tecnico2 / Demo1234!")

    def _reset_demo_data(self):
        OrdenRepuesto.objects.filter(orden__equipo__cliente__email__endswith="@demo.local").delete()
        OrdenReparacion.objects.filter(equipo__cliente__email__endswith="@demo.local").delete()
        Equipo.objects.filter(cliente__email__endswith="@demo.local").delete()
        Cliente.objects.filter(email__endswith="@demo.local").delete()
        Repuesto.objects.filter(sku__startswith="DEMO-").delete()

        user_model = get_user_model()
        user_model.objects.filter(username__in=["demo_owner", "demo_tecnico1", "demo_tecnico2"]).delete()

        self.stdout.write(self.style.WARNING("Datos demo anteriores eliminados."))

    def _seed_users(self):
        user_model = get_user_model()

        owner, _ = user_model.objects.get_or_create(
            username="demo_owner",
            defaults={
                "email": "owner@demo.local",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        owner.set_password("Demo1234!")
        owner.is_staff = True
        owner.is_superuser = True
        owner.save(update_fields=["password", "is_staff", "is_superuser"])

        tech1, _ = user_model.objects.get_or_create(
            username="demo_tecnico1",
            defaults={"email": "tecnico1@demo.local", "is_staff": True},
        )
        tech1.set_password("Demo1234!")
        tech1.is_staff = True
        tech1.save(update_fields=["password", "is_staff"])

        tech2, _ = user_model.objects.get_or_create(
            username="demo_tecnico2",
            defaults={"email": "tecnico2@demo.local", "is_staff": True},
        )
        tech2.set_password("Demo1234!")
        tech2.is_staff = True
        tech2.save(update_fields=["password", "is_staff"])

        PerfilUsuario.objects.update_or_create(usuario=owner, defaults={"rol": PerfilUsuario.Rol.DUENO})
        PerfilUsuario.objects.update_or_create(usuario=tech1, defaults={"rol": PerfilUsuario.Rol.TECNICO})
        PerfilUsuario.objects.update_or_create(usuario=tech2, defaults={"rol": PerfilUsuario.Rol.TECNICO})

        return owner, tech1, tech2

    def _seed_clientes(self):
        raw_clientes = [
            ("Juan Pérez", "2604001001", "juan@demo.local", "Av. Roca 123"),
            ("María Gómez", "2604001002", "maria@demo.local", "Belgrano 456"),
            ("Lucas Díaz", "2604001003", "lucas@demo.local", "San Martín 987"),
        ]
        clientes = {}
        for nombre, telefono, email, direccion in raw_clientes:
            cliente, _ = Cliente.objects.get_or_create(
                email=email,
                defaults={"nombre": nombre, "telefono": telefono, "direccion": direccion},
            )
            clientes[email] = cliente
        return clientes

    def _seed_equipos(self, clientes):
        raw_equipos = [
            ("juan@demo.local", "Notebook", "Lenovo", "ThinkPad T14", "SN-DEMO-001"),
            ("maria@demo.local", "Notebook", "HP", "Pavilion 15", "SN-DEMO-002"),
            ("lucas@demo.local", "PC", "Custom", "Ryzen 5600", "SN-DEMO-003"),
        ]
        equipos = {}
        for email, tipo, marca, modelo, serie in raw_equipos:
            equipo, _ = Equipo.objects.get_or_create(
                numero_serie=serie,
                defaults={
                    "cliente": clientes[email],
                    "tipo": tipo,
                    "marca": marca,
                    "modelo": modelo,
                    "observaciones_ingreso": "Ingreso demo para presentación",
                },
            )
            equipos[serie] = equipo
        return equipos

    def _seed_repuestos(self):
        raw_repuestos = [
            ("DEMO-SSD-480", "SSD 480GB", 8, Decimal("52000.00")),
            ("DEMO-RAM-8", "Memoria RAM 8GB", 12, Decimal("34000.00")),
            ("DEMO-BAT-HP", "Batería HP Pavilion", 5, Decimal("68000.00")),
            ("DEMO-FAN-LEN", "Cooler Lenovo T14", 3, Decimal("29000.00")),
        ]

        repuestos = {}
        for sku, nombre, stock, precio in raw_repuestos:
            repuesto, _ = Repuesto.objects.update_or_create(
                sku=sku,
                defaults={
                    "nombre": nombre,
                    "descripcion": "Repuesto demo",
                    "stock_actual": stock,
                    "stock_minimo": 2,
                    "precio_unitario": precio,
                    "activo": True,
                },
            )
            repuestos[sku] = repuesto

        return repuestos

    def _seed_ordenes(self, equipos, repuestos, tech1, tech2):
        orden_specs = [
            {
                "serie": "SN-DEMO-001",
                "problema": "No enciende correctamente",
                "diagnostico": "Falla en unidad de almacenamiento",
                "precio": Decimal("78000.00"),
                "estado": OrdenReparacion.Estado.EN_REVISION,
                "tecnico": tech1,
                "items": [("DEMO-SSD-480", 1, Decimal("52000.00"))],
            },
            {
                "serie": "SN-DEMO-002",
                "problema": "Batería dura muy poco",
                "diagnostico": "Batería degradada, requiere reemplazo",
                "precio": Decimal("92000.00"),
                "estado": OrdenReparacion.Estado.REPARANDO,
                "tecnico": tech2,
                "items": [("DEMO-BAT-HP", 1, Decimal("68000.00"))],
            },
            {
                "serie": "SN-DEMO-003",
                "problema": "Reinicio aleatorio",
                "diagnostico": "Módulo RAM defectuoso",
                "precio": Decimal("45000.00"),
                "estado": OrdenReparacion.Estado.PRESUPUESTADO,
                "tecnico": tech1,
                "items": [("DEMO-RAM-8", 1, Decimal("34000.00"))],
            },
        ]

        for spec in orden_specs:
            orden, created = OrdenReparacion.objects.get_or_create(
                equipo=equipos[spec["serie"]],
                problema_reportado=spec["problema"],
                defaults={
                    "diagnostico": spec["diagnostico"],
                    "precio_estimado": spec["precio"],
                    "estado": spec["estado"],
                    "tecnico_asignado": spec["tecnico"],
                },
            )

            if not created:
                orden.diagnostico = spec["diagnostico"]
                orden.precio_estimado = spec["precio"]
                orden.estado = spec["estado"]
                orden.tecnico_asignado = spec["tecnico"]
                orden.save()

            if not orden.repuestos.exists():
                for sku, cantidad, precio in spec["items"]:
                    OrdenRepuesto.objects.create(
                        orden=orden,
                        repuesto=repuestos[sku],
                        cantidad=cantidad,
                        precio_unitario=precio,
                    )
