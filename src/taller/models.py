import uuid
from io import BytesIO

import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models, transaction

from inventario.models import MovimientoStock


class Cliente(models.Model):
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    direccion = models.CharField(max_length=180, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.telefono}"


class Equipo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="equipos")
    tipo = models.CharField(max_length=60, default="Notebook")
    marca = models.CharField(max_length=80)
    modelo = models.CharField(max_length=80)
    numero_serie = models.CharField(max_length=120, blank=True)
    observaciones_ingreso = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} {self.marca} {self.modelo}"


class OrdenReparacion(models.Model):
    class Estado(models.TextChoices):
        INGRESADO = "INGRESADO", "Ingresado"
        EN_REVISION = "EN_REVISION", "En revisión"
        PRESUPUESTADO = "PRESUPUESTADO", "Presupuestado"
        REPARANDO = "REPARANDO", "Reparando"
        REPARADO = "REPARADO", "Reparado"
        ENTREGADO = "ENTREGADO", "Entregado"
        CANCELADO = "CANCELADO", "Cancelado"

    equipo = models.ForeignKey(Equipo, on_delete=models.PROTECT, related_name="ordenes")
    tecnico_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordenes_asignadas",
    )
    problema_reportado = models.TextField()
    diagnostico = models.TextField(blank=True)
    precio_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.INGRESADO)
    stock_descontado = models.BooleanField(default=False)
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    qr_imagen = models.ImageField(upload_to="qr/", blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Orden #{self.pk} - {self.equipo}"

    @property
    def url_seguimiento(self):
        base = settings.SITE_BASE_URL.rstrip("/")
        return f"{base}/seguimiento/{self.qr_token}/"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new or not self.qr_imagen:
            self.generar_qr()

    def generar_qr(self):
        qr_img = qrcode.make(self.url_seguimiento)
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        self.qr_imagen.save(
            f"orden_{self.pk}.png",
            ContentFile(buffer.getvalue()),
            save=False,
        )
        super().save(update_fields=["qr_imagen"])

    @transaction.atomic
    def descontar_stock_repuestos(self):
        if self.stock_descontado:
            return

        items = self.repuestos.select_related("repuesto")
        for item in items:
            item.repuesto.descontar_stock(item.cantidad)
            MovimientoStock.objects.create(
                repuesto=item.repuesto,
                tipo=MovimientoStock.Tipo.SALIDA,
                cantidad=item.cantidad,
                motivo=f"Orden de reparación #{self.pk}",
            )

        self.stock_descontado = True
        super().save(update_fields=["stock_descontado"])


class OrdenRepuesto(models.Model):
    orden = models.ForeignKey(OrdenReparacion, on_delete=models.CASCADE, related_name="repuestos")
    repuesto = models.ForeignKey("inventario.Repuesto", on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.repuesto.nombre} x{self.cantidad} (Orden #{self.orden_id})"

    def subtotal(self):
        return self.cantidad * self.precio_unitario