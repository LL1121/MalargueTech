from django import forms

from inventario.models import Repuesto
from taller.models import Cliente, Equipo, OrdenReparacion, OrdenRepuesto


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            base_class = "form-control"
            if isinstance(field.widget, forms.Select):
                base_class = "form-select"
            if isinstance(field.widget, forms.CheckboxInput):
                base_class = "form-check-input"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {base_class}".strip()


class ClienteForm(StyledModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "telefono", "email", "direccion"]


class EquipoForm(StyledModelForm):
    class Meta:
        model = Equipo
        fields = [
            "cliente",
            "tipo",
            "marca",
            "modelo",
            "numero_serie",
            "observaciones_ingreso",
        ]


class OrdenReparacionForm(StyledModelForm):
    class Meta:
        model = OrdenReparacion
        fields = [
            "equipo",
            "tecnico_asignado",
            "problema_reportado",
            "diagnostico",
            "precio_estimado",
            "estado",
        ]


class RepuestoForm(StyledModelForm):
    class Meta:
        model = Repuesto
        fields = [
            "nombre",
            "sku",
            "descripcion",
            "stock_actual",
            "stock_minimo",
            "precio_unitario",
            "activo",
        ]


class EstadoOrdenForm(StyledModelForm):
    class Meta:
        model = OrdenReparacion
        fields = ["estado", "diagnostico", "precio_estimado", "tecnico_asignado"]


class OrdenRepuestoForm(StyledModelForm):
    repuesto = forms.ModelChoiceField(queryset=Repuesto.objects.filter(activo=True))

    class Meta:
        model = OrdenRepuesto
        fields = ["repuesto", "cantidad", "precio_unitario"]