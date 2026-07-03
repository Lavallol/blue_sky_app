from django.shortcuts import render, get_object_or_404, redirect
from .models import Produccion, ProduccionLinea
from .forms import ProduccionForm

def produccion_lista(request):
    producciones = Produccion.objects.all().order_by('-fecha')
    return render(request, 'produccion/lista.html', {'producciones': producciones})


def produccion_crear(request):
    if request.method == 'POST':
        form = ProduccionForm(request.POST)

        if form.is_valid():
            # 1. Guardamos la producción
            produccion = form.save()

            # 2. Obtenemos el escandallo asociado
            escandallo = produccion.escandallo

            # 3. Recorremos las líneas del escandallo y creamos líneas teóricas
            for linea in escandallo.lineas.all():
                ProduccionLinea.objects.create(
                    produccion=produccion,
                    ingrediente=linea.producto,
                    cantidad_teorica=linea.cantidad * produccion.rendimiento_real,
                    cantidad_real=0,   # El usuario podrá editarlo después
                    unidad=linea.unidad,
                    merma=0
                )

            return redirect('produccion_detalle', pk=produccion.pk)

    else:
        form = ProduccionForm()

    return render(request, 'produccion/crear.html', {
        'form': form,
    })


def produccion_detalle(request, pk):
    produccion = get_object_or_404(Produccion, pk=pk)
    lineas = ProduccionLinea.objects.filter(produccion=produccion)
    return render(request, 'produccion/detalle.html', {
        'produccion': produccion,
        'lineas': lineas
    })