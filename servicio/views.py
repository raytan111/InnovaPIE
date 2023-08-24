from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from index.forms import *
from index.models import Servicio
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def regservicio(request):
    data = {
        'form': ServicioForm()
    }

    if request.method == "POST":
        formulario = ServicioForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            #data['mensaje'] = "Se ha guardado el cliente correctamente"
            return redirect("Lista Servicio")
    return render(request, "servicio/regservicio.html", data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def listaservicio(request):
    servicio = Servicio.objects.all()
    data = {
        'servicio': servicio
    }
    return render(request, "servicio/listaservicio.html", data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def editarservicio(request, id):
    servicio = Servicio.objects.get(id=id)
    form = ServicioForm(instance=servicio)

    if request.method == "POST":
        form = ServicioForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            # Agregar un mensaje de éxito si se desea
            return redirect("Lista Servicio")

    data = {
        'form': form
    }
    return render(request, "servicio/editarservicio.html", data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def eliminar_servicio(request, servicio_id):
    servicio = Servicio.objects.get(id=servicio_id)
    
    # Verificar si el cliente existe
    if servicio:
        # Eliminar al cliente
        servicio.delete()
        messages.success(request, 'El Servicio se eliminó correctamente.')
    else:
        messages.error(request, 'No se encontró el Servicio especificado.')
    
    return redirect('Lista Servicio')