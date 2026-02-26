from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from usuarios.models import PerfilUsuario


@receiver(post_save, sender=get_user_model())
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)