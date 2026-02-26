from django.contrib import admin

from inventario.models import MovimientoStock, Repuesto


@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "sku", "stock_actual", "stock_minimo", "precio_unitario", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre", "sku")


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ("repuesto", "tipo", "cantidad", "motivo", "creado_en")
    list_filter = ("tipo", "creado_en")
    search_fields = ("repuesto__nombre", "repuesto__sku", "motivo")