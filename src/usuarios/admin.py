from django.contrib import admin

from usuarios.models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol", "activo", "creado_en")
    list_filter = ("rol", "activo")
    search_fields = ("usuario__username", "usuario__email")