from django.core.exceptions import ValidationError
from django.test import TestCase

from inventario.models import Repuesto


class RepuestoTests(TestCase):
    def test_descuento_stock_ok(self):
        repuesto = Repuesto.objects.create(
            nombre="Disco SSD 500GB",
            sku="SSD-500",
            stock_actual=5,
            stock_minimo=1,
            precio_unitario="100000.00",
        )

        repuesto.descontar_stock(2)
        repuesto.refresh_from_db()

        self.assertEqual(repuesto.stock_actual, 3)

    def test_descuento_stock_insuficiente(self):
        repuesto = Repuesto.objects.create(
            nombre="Memoria RAM 8GB",
            sku="RAM-8",
            stock_actual=1,
            stock_minimo=1,
            precio_unitario="40000.00",
        )

        with self.assertRaises(ValidationError):
            repuesto.descontar_stock(2)