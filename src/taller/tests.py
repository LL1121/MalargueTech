from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from inventario.models import MovimientoStock, Repuesto
from taller.models import Cliente, Equipo, OrdenReparacion, OrdenRepuesto


class TallerFlujoTests(TestCase):
    def setUp(self):
        self.tecnico = get_user_model().objects.create_user(
            username="tecnico1",
            password="pass1234",
            email="tecnico@malarguetech.local",
        )
        self.cliente = Cliente.objects.create(
            nombre="Juan Perez",
            telefono="2604000000",
            email="juan@example.com",
        )
        self.equipo = Equipo.objects.create(
            cliente=self.cliente,
            tipo="Notebook",
            marca="Lenovo",
            modelo="ThinkPad",
        )
        self.repuesto = Repuesto.objects.create(
            nombre="Bateria",
            sku="BAT-THINK",
            stock_actual=3,
            stock_minimo=1,
            precio_unitario="30000.00",
        )

    def test_reparado_descuenta_stock_y_genera_movimiento(self):
        orden = OrdenReparacion.objects.create(
            equipo=self.equipo,
            tecnico_asignado=self.tecnico,
            problema_reportado="No enciende",
            estado=OrdenReparacion.Estado.INGRESADO,
        )
        OrdenRepuesto.objects.create(
            orden=orden,
            repuesto=self.repuesto,
            cantidad=2,
            precio_unitario="30000.00",
        )

        orden.estado = OrdenReparacion.Estado.REPARADO
        orden.save()

        self.repuesto.refresh_from_db()
        orden.refresh_from_db()

        self.assertEqual(self.repuesto.stock_actual, 1)
        self.assertTrue(orden.stock_descontado)
        self.assertEqual(MovimientoStock.objects.filter(repuesto=self.repuesto).count(), 1)

    def test_cambio_estado_envia_email(self):
        orden = OrdenReparacion.objects.create(
            equipo=self.equipo,
            tecnico_asignado=self.tecnico,
            problema_reportado="Pantalla rota",
            estado=OrdenReparacion.Estado.INGRESADO,
        )

        orden.estado = OrdenReparacion.Estado.EN_REVISION
        orden.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Actualización de tu equipo", mail.outbox[0].subject)

    def test_seguimiento_publico_con_qr(self):
        orden = OrdenReparacion.objects.create(
            equipo=self.equipo,
            tecnico_asignado=self.tecnico,
            problema_reportado="Teclado falla",
            estado=OrdenReparacion.Estado.EN_REVISION,
        )

        response = self.client.get(reverse("seguimiento_publico", args=[orden.qr_token]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Juan Perez")

    def test_dashboard_requiere_autenticacion(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/cuentas/login/", response.url)