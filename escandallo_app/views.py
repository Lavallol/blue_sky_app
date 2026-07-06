from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Escandallo, EscandalloLinea
from .forms import EscandalloForm, EscandalloLineaForm
from inventario_app.models import Producto

# 🔧 IMPORTACIÓN AÑADIDA
from escandallo_app.utils.utils import normalizar_decimal


# =========================================================
# LISTA
# =========================================================
def escandallo_list(request):
    escandallos = Escandallo.objects.all()
    return render(request, 'escandallo_app/lista.html', {
        'escandallos': escandallos
    })


# =========================================================
# DETALLE
# =========================================================
def escandallo_detalle(request, pk):
    escandallo = get_object_or_404(Escandallo, pk=pk)
    lineas = escandallo.lineas.all()
    return render(request, 'escandallo_app/detalle.html', {
        'escandallo': escandallo,
        'lineas': lineas
    })


# =========================================================
# CREAR
# =========================================================
def escandallo_crear(request):
    if request.method == 'POST':
        form = EscandalloForm(request.POST)
        if form.is_valid():
            escandallo = form.save()
            return redirect('escandallo_detalle', pk=escandallo.pk)
    else:
        form = EscandalloForm()

    return render(request, 'escandallo_app/form.html', {
        'form': form,
        'titulo': 'Crear escandallo'
    })


# =========================================================
# EDITAR
# =========================================================
def escandallo_editar(request, pk):
    escandallo = get_object_or_404(Escandallo, pk=pk)

    if request.method == 'POST':
        form = EscandalloForm(request.POST, instance=escandallo)
        if form.is_valid():
            form.save()
            return redirect('escandallo_detalle', pk=escandallo.pk)
    else:
        form = EscandalloForm(instance=escandallo)

    return render(request, 'escandallo_app/form.html', {
        'form': form,
        'titulo': 'Editar escandallo'
    })


# =========================================================
# ELIMINAR
# =========================================================
def escandallo_eliminar(request, pk):
    escandallo = get_object_or_404(Escandallo, pk=pk)

    if request.method == 'POST':
        escandallo.delete()
        return redirect('escandallo_list')

    return render(request, 'escandallo_app/eliminar.html', {
        'escandallo': escandallo
    })


# =========================================================
# INGREDIENTE — CREAR
# =========================================================
def escandallo_ingrediente_crear(request, escandallo_id):
    escandallo = get_object_or_404(Escandallo, id=escandallo_id)

    if request.method == 'POST':
        form = EscandalloLineaForm(request.POST)
        if form.is_valid():
            linea = form.save(commit=False)
            linea.escandallo = escandallo
            linea.save()
            return redirect('escandallo_detalle', escandallo.id)
    else:
        form = EscandalloLineaForm()

    return render(request, 'escandallo_app/ingrediente_form.html', {
        'form': form,
        'escandallo': escandallo,
        'editar': False
    })


# =========================================================
# INGREDIENTE — EDITAR
# =========================================================
def escandallo_ingrediente_editar(request, linea_id):
    linea = get_object_or_404(EscandalloLinea, id=linea_id)
    escandallo = linea.escandallo

    if request.method == 'POST':
        form = EscandalloLineaForm(request.POST, instance=linea)
        if form.is_valid():
            form.save()
            return redirect('escandallo_detalle', escandallo.id)
    else:
        form = EscandalloLineaForm(instance=linea)

    return render(request, 'escandallo_app/ingrediente_form.html', {
        'form': form,
        'escandallo': escandallo,
        'editar': True
    })


# =========================================================
# INGREDIENTE — ELIMINAR
# =========================================================
def escandallo_ingrediente_eliminar(request, linea_id):
    linea = get_object_or_404(EscandalloLinea, id=linea_id)
    escandallo = linea.escandallo

    if request.method == 'POST':
        linea.delete()
        return redirect('escandallo_detalle', escandallo.id)

    return render(request, 'escandallo_app/ingrediente_eliminar.html', {
        'linea': linea,
        'escandallo': escandallo
    })


# =========================================================
# NUEVO: AUTOCOMPLETAR PRECIO DEL PRODUCTO
# =========================================================
def obtener_precio_producto(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)

        # 🔧 NORMALIZACIÓN AÑADIDA
        precio = normalizar_decimal(producto.precio_compra)

        return JsonResponse({"precio": precio})

    except Producto.DoesNotExist:
        return JsonResponse({"precio": 0})
