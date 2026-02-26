from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from taller.models import OrdenReparacion


@receiver(pre_save, sender=OrdenReparacion)
def registrar_estado_anterior(sender, instance, **kwargs):
    if not instance.pk:
        instance._estado_anterior = None
        return
    previo = OrdenReparacion.objects.filter(pk=instance.pk).only("estado").first()
    instance._estado_anterior = previo.estado if previo else None


@receiver(post_save, sender=OrdenReparacion)
def flujo_automatico_orden(sender, instance, created, **kwargs):
    estado_anterior = getattr(instance, "_estado_anterior", None)
    cambio_estado = estado_anterior is not None and estado_anterior != instance.estado

    if instance.estado == OrdenReparacion.Estado.REPARADO and not instance.stock_descontado:
        instance.descontar_stock_repuestos()

    if not cambio_estado:
        return

    cliente_email = instance.equipo.cliente.email
    if not cliente_email:
        return

    send_mail(
        subject=f"Actualización de tu equipo - Orden #{instance.pk}",
        message=(
            f"Hola {instance.equipo.cliente.nombre},\n\n"
            f"Tu equipo ({instance.equipo}) cambió a estado: {instance.get_estado_display()}.\n"
            f"Podés seguir el detalle aquí: {instance.url_seguimiento}\n\n"
            "Malargüe Tech"
        ),
        from_email=None,
        recipient_list=[cliente_email],
        fail_silently=True,
    )