from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.forms import inlineformset_factory
from django.conf import settings
from django.db.models.deletion import ProtectedError
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from inventario.models import Repuesto
from taller.forms import (
    ClienteForm,
    EquipoForm,
    EstadoOrdenForm,
    OrdenReparacionForm,
    OrdenRepuestoForm,
    RepuestoForm,
)
from taller.models import Cliente, Equipo, OrdenReparacion, OrdenRepuesto


BADGE_BY_ESTADO = {
    OrdenReparacion.Estado.INGRESADO: "ingresado",
    OrdenReparacion.Estado.EN_REVISION: "revision",
    OrdenReparacion.Estado.PRESUPUESTADO: "presupuestado",
    OrdenReparacion.Estado.REPARANDO: "reparando",
    OrdenReparacion.Estado.REPARADO: "reparado",
    OrdenReparacion.Estado.ENTREGADO: "entregado",
    OrdenReparacion.Estado.CANCELADO: "cancelado",
}


def health(_request):
    return HttpResponse("ok")


def home(request):
    accesos = [
        {"titulo": "Órdenes", "descripcion": "Ver y gestionar reparaciones", "url": reverse("ordenes_list")},
        {"titulo": "Equipos", "descripcion": "Equipos ingresados al taller", "url": reverse("equipos_list")},
        {"titulo": "Repuestos", "descripcion": "Stock y disponibilidad", "url": reverse("repuestos_list")},
        {"titulo": "Clientes", "descripcion": "Datos de contacto y equipos", "url": reverse("clientes_list")},
    ]
    return render(request, "taller/home.html", {"accesos": accesos})


@login_required
def dashboard(request):
    ordenes = OrdenReparacion.objects.select_related("equipo__cliente", "tecnico_asignado").order_by("-actualizado_en")
    stock_bajo = Repuesto.objects.filter(activo=True, stock_actual__lte=0) | Repuesto.objects.filter(
        activo=True, stock_actual__lte=1
    )
    estadisticas_estados = (
        OrdenReparacion.objects.values("estado")
        .annotate(total=Count("id"))
        .order_by("estado")
    )
    facturacion_estim = OrdenReparacion.objects.filter(
        estado__in=[OrdenReparacion.Estado.REPARADO, OrdenReparacion.Estado.ENTREGADO]
    ).aggregate(total=Sum("precio_estimado"))["total"]
    return render(
        request,
        "taller/dashboard.html",
        {
            "ordenes": ordenes,
            "stock_bajo": stock_bajo[:8],
            "estadisticas_estados": estadisticas_estados,
            "facturacion_estim": facturacion_estim or 0,
        },
    )


@login_required
def clientes_list(request):
    clientes = Cliente.objects.order_by("-creado_en")
    return render(request, "taller/clientes_list.html", {"clientes": clientes})


@login_required
def equipos_list(request):
    equipos = Equipo.objects.select_related("cliente").order_by("-creado_en")
    return render(request, "taller/equipos_list.html", {"equipos": equipos})


@login_required
def repuestos_list(request):
    repuestos = Repuesto.objects.order_by("nombre")
    return render(request, "taller/repuestos_list.html", {"repuestos": repuestos})


@login_required
def ordenes_list(request):
    ordenes = OrdenReparacion.objects.select_related("equipo__cliente", "tecnico_asignado").order_by("-creado_en")
    return render(
        request,
        "taller/ordenes_list.html",
        {
            "ordenes": ordenes,
            "badge_by_estado": BADGE_BY_ESTADO,
        },
    )


@login_required
def cliente_create(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente creado correctamente.")
            return redirect("clientes_list")
    else:
        form = ClienteForm()
    return render(request, "taller/form_page.html", {"title": "Nuevo cliente", "form": form})




@login_required
def cliente_edit(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente actualizado correctamente.")
            return redirect("clientes_list")
    else:
        form = ClienteForm(instance=cliente)
    return render(request, "taller/form_page.html", {"title": "Editar cliente", "form": form})
@login_required
def equipo_create(request):
    next_url = request.GET.get("next") or request.POST.get("next")
    if request.method == "POST":
        form = EquipoForm(request.POST)
        if form.is_valid():
            equipo = form.save()
            messages.success(request, "Equipo creado correctamente.")
            if next_url == "orden_create_form":
                return redirect(f"{reverse('orden_create_form')}?equipo={equipo.id}")
            return redirect("equipos_list")
    else:
        form = EquipoForm()
    return render(
        request,
        "taller/form_page.html",
        {"title": "Nuevo equipo", "form": form, "next": next_url},
    )




@login_required
def equipo_edit(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    if request.method == "POST":
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipo actualizado correctamente.")
            return redirect("equipos_list")
    else:
        form = EquipoForm(instance=equipo)
    return render(request, "taller/form_page.html", {"title": "Editar equipo", "form": form})
@login_required
def repuesto_create(request):
    if request.method == "POST":
        form = RepuestoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Repuesto creado correctamente.")
            return redirect("repuestos_list")
    else:
        form = RepuestoForm()
    return render(request, "taller/form_page.html", {"title": "Nuevo repuesto", "form": form})




@login_required
def repuesto_edit(request, pk):
    repuesto = get_object_or_404(Repuesto, pk=pk)
    if request.method == "POST":
        form = RepuestoForm(request.POST, instance=repuesto)
        if form.is_valid():
            form.save()
            messages.success(request, "Repuesto actualizado correctamente.")
            return redirect("repuestos_list")
    else:
        form = RepuestoForm(instance=repuesto)
    return render(request, "taller/form_page.html", {"title": "Editar repuesto", "form": form})
@login_required
def orden_create(request):
    equipos = Equipo.objects.select_related("cliente").order_by("-creado_en")
    return render(request, "taller/orden_select_equipo.html", {"equipos": equipos})


@login_required
def orden_create_form(request):
    OrdenRepuestoFormSet = inlineformset_factory(
        OrdenReparacion,
        OrdenRepuesto,
        form=OrdenRepuestoForm,
        extra=1,
        can_delete=True,
    )
    equipo_id = request.GET.get("equipo")

    if request.method == "POST":
        form = OrdenReparacionForm(request.POST)
        formset = OrdenRepuestoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            stock_ok = True
            for repuesto_form in formset.forms:
                cleaned = getattr(repuesto_form, "cleaned_data", None)
                if not cleaned or cleaned.get("DELETE"):
                    continue
                repuesto = cleaned.get("repuesto")
                cantidad = cleaned.get("cantidad") or 0
                if repuesto and cantidad > repuesto.stock_actual:
                    repuesto_form.add_error(
                        "cantidad",
                        f"Stock insuficiente para {repuesto.nombre}. Disponible: {repuesto.stock_actual}.",
                    )
                    stock_ok = False

            if stock_ok:
                orden = form.save()
                formset.instance = orden
                formset.save()
                messages.success(request, f"Orden #{orden.id} creada correctamente.")
                return redirect(reverse("orden_detalle", args=[orden.id]))
    else:
        initial = {}
        if equipo_id:
            initial["equipo"] = equipo_id
        form = OrdenReparacionForm(initial=initial)
        formset = OrdenRepuestoFormSet()

    return render(
        request,
        "taller/orden_form.html",
        {
            "title": "Nueva orden",
            "form": form,
            "formset": formset,
        },
    )


@login_required
def orden_detalle(request, pk):
    orden = get_object_or_404(
        OrdenReparacion.objects.select_related("equipo__cliente", "tecnico_asignado"),
        pk=pk,
    )
    estado_form = EstadoOrdenForm(instance=orden)
    repuesto_form = OrdenRepuestoForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_estado":
            estado_form = EstadoOrdenForm(request.POST, instance=orden)
            if estado_form.is_valid():
                estado_form.save()
                messages.success(request, "Orden actualizada.")
                return redirect(reverse("orden_detalle", args=[orden.id]))
        elif action == "add_repuesto":
            repuesto_form = OrdenRepuestoForm(request.POST)
            if repuesto_form.is_valid():
                item = repuesto_form.save(commit=False)
                if item.cantidad > item.repuesto.stock_actual:
                    repuesto_form.add_error(
                        "cantidad",
                        f"Stock insuficiente para {item.repuesto.nombre}. Disponible: {item.repuesto.stock_actual}.",
                    )
                else:
                    item.orden = orden
                    item.save()
                    messages.success(request, "Repuesto agregado a la orden.")
                    return redirect(reverse("orden_detalle", args=[orden.id]))

    total_repuestos = sum((item.subtotal() for item in orden.repuestos.all()), start=0)
    return render(
        request,
        "taller/orden_detalle.html",
        {
            "orden": orden,
            "estado_form": estado_form,
            "repuesto_form": repuesto_form,
            "total_repuestos": total_repuestos,
            "badge": BADGE_BY_ESTADO.get(orden.estado, "secondary"),
        },
    )


@login_required
def orden_edit(request, pk):
    orden = get_object_or_404(OrdenReparacion, pk=pk)
    if request.method == "POST":
        form = OrdenReparacionForm(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            messages.success(request, "Orden actualizada correctamente.")
            return redirect("ordenes_list")
    else:
        form = OrdenReparacionForm(instance=orden)
    return render(request, "taller/form_page.html", {"title": "Editar orden", "form": form})


def seguimiento_publico(request, token):
    orden = get_object_or_404(
        OrdenReparacion.objects.select_related("equipo__cliente", "tecnico_asignado"),
        qr_token=token,
    )
    return render(
        request,
        "taller/seguimiento_publico.html",
        {
            "orden": orden,
            "badge": BADGE_BY_ESTADO.get(orden.estado, "secondary"),
            "repuestos": orden.repuestos.select_related("repuesto"),
        },
    )


@login_required
@require_POST
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    try:
        cliente.delete()
        messages.success(request, "Cliente eliminado correctamente.")
    except ProtectedError:
        messages.error(request, "No se puede eliminar el cliente porque tiene datos asociados protegidos.")
    return redirect("clientes_list")


@login_required
@require_POST
def equipo_delete(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    try:
        equipo.delete()
        messages.success(request, "Equipo eliminado correctamente.")
    except ProtectedError:
        messages.error(request, "No se puede eliminar el equipo porque está asociado a órdenes de reparación.")
    return redirect("equipos_list")


@login_required
@require_POST
def repuesto_delete(request, pk):
    repuesto = get_object_or_404(Repuesto, pk=pk)
    try:
        repuesto.delete()
        messages.success(request, "Repuesto eliminado correctamente.")
    except ProtectedError:
        messages.error(request, "No se puede eliminar el repuesto porque está en uso en órdenes o movimientos.")
    return redirect("repuestos_list")


@login_required
@require_POST
def orden_delete(request, pk):
    orden = get_object_or_404(OrdenReparacion, pk=pk)
    orden.delete()
    messages.success(request, "Orden eliminada correctamente.")
    return redirect("ordenes_list")


@login_required
def seed_demo_button(request):
    if request.method != "POST":
        raise PermissionDenied("Método no permitido")

    if not settings.DEBUG or not request.user.is_superuser:
        raise PermissionDenied("No autorizado")

    call_command("seed_demo", "--reset")
    messages.success(request, "Datos demo recargados correctamente.")
    return redirect(request.POST.get("next") or "home")