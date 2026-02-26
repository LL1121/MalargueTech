from django.contrib import admin

from taller.models import Cliente, Equipo, OrdenReparacion, OrdenRepuesto


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "telefono", "email", "creado_en")
    search_fields = ("nombre", "telefono", "email")


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "marca", "modelo", "numero_serie", "cliente", "creado_en")
    list_filter = ("tipo", "marca")
    search_fields = ("marca", "modelo", "numero_serie", "cliente__nombre")


class OrdenRepuestoInline(admin.TabularInline):
    model = OrdenRepuesto
    extra = 1


@admin.register(OrdenReparacion)
class OrdenReparacionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "equipo",
        "tecnico_asignado",
        "estado",
        "precio_estimado",
        "stock_descontado",
        "creado_en",
    )
    list_filter = ("estado", "stock_descontado", "creado_en")
    search_fields = ("equipo__marca", "equipo__modelo", "equipo__cliente__nombre", "problema_reportado")
    inlines = [OrdenRepuestoInline]
    readonly_fields = ("qr_token", "qr_imagen")


@admin.register(OrdenRepuesto)
class OrdenRepuestoAdmin(admin.ModelAdmin):
    list_display = ("orden", "repuesto", "cantidad", "precio_unitario")
    list_filter = ("repuesto",)
    search_fields = ("orden__id", "repuesto__nombre", "repuesto__sku")