from django.core.exceptions import ValidationError
from django.db import models


class Repuesto(models.Model):
    nombre = models.CharField(max_length=120)
    sku = models.CharField(max_length=60, unique=True)
    descripcion = models.TextField(blank=True)
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=0)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

    def descontar_stock(self, cantidad):
        if cantidad > self.stock_actual:
            raise ValidationError(
                f"Stock insuficiente para {self.nombre}. Disponible: {self.stock_actual}, requerido: {cantidad}."
            )
        self.stock_actual -= cantidad
        self.save(update_fields=["stock_actual"])


class MovimientoStock(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SALIDA = "SALIDA", "Salida"

    repuesto = models.ForeignKey(Repuesto, on_delete=models.PROTECT, related_name="movimientos")
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    cantidad = models.PositiveIntegerField()
    motivo = models.CharField(max_length=180, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.repuesto.sku} x{self.cantidad}"