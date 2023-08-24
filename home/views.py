from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from index.models import PerfilUsuario, DatosTransferencia, Documento
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from index.forms import PerfilUsuarioForm, DatosTransferenciaForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, FileResponse
import json
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, "home/home.html")

@login_required
def ver_perfil_usuario(request):
    # Obtener el perfil del usuario basado en el usuario autenticado
    usuario = get_object_or_404(User, id=request.user.id)
    perfil_usuario = get_object_or_404(PerfilUsuario, usuario=usuario)
    datos_transferencia = DatosTransferencia.objects.get(d_usuario=usuario)
    documentos = Documento.objects.filter(perfil=perfil_usuario)

    return render(request, 'home/perfil_usuario.html', {
        'perfil_usuario': perfil_usuario,
        'datos_transferencia': datos_transferencia,
        'documentos': documentos,
        'usuario': usuario,
    })

@login_required
def editar_perfil_usuario(request):
    usuario = get_object_or_404(User, id=request.user.id)
    perfil = get_object_or_404(PerfilUsuario, usuario=usuario)
    datos = get_object_or_404(DatosTransferencia, d_usuario=usuario)

    if request.method == 'POST':
        perfil_form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        datos_transferencia_form = DatosTransferenciaForm(request.POST, instance=datos)
        
        if perfil_form.is_valid() and datos_transferencia_form.is_valid():
            perfil_form.save()
            datos_transferencia_form.save()
            return redirect('perfil_usuario', id=usuario.id)

    else:
        perfil_form = PerfilUsuarioForm(instance=perfil)
        datos_transferencia_form = DatosTransferenciaForm(instance=datos)

    return render(request, 'home/editar_perfil.html', {
        'perfil_usuario': perfil, 
        'datos_transferencia': datos, 
        'perfil_form': perfil_form, 
        'datos_transferencia_form': datos_transferencia_form,
        'usuario': usuario,
    })

@login_required
def nuevo_documento(request, id):
    perfil_usuario = get_object_or_404(PerfilUsuario, id=id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        archivo = request.FILES.get('archivo')
        descripcion = request.POST.get('descripcion')

        if nombre and archivo and descripcion:
            nuevo_documento = Documento(nombre=nombre, archivo=archivo, descripcion=descripcion, perfil=perfil_usuario)
            nuevo_documento.save()
            return redirect('perfil_usuario', id=perfil_usuario.usuario.id)
        else:
            return render(request, 'error.html', {'mensaje': 'Por favor completa todos los campos del formulario'})

    return render(request, 'colaboradores/nuevo_documento.html', {'perfil_usuario': perfil_usuario})


@csrf_exempt
@login_required
def eliminar_documento(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        documento_id = data.get('id')

        try:
            documento = Documento.objects.get(id=documento_id)
            documento.delete()

            return JsonResponse({'success': True})

        except Documento.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Documento no encontrado.'})
    else:
        return JsonResponse({'success': False, 'error': 'Método no permitido.'})
    

@login_required
def descargar_documento(request, documento_id):
    # Obtén el objeto Documento, o lanza un 404 si no se encuentra
    documento = get_object_or_404(Documento, id=documento_id)

    # Realiza cualquier lógica adicional necesaria, como verificar permisos, etc.

    # Obtén el archivo del Documento
    archivo_documento = documento.archivo

    # Crea una respuesta HTTP con el archivo adjunto
    response = FileResponse(archivo_documento.open(), content_type='application/octet-stream')  # Establece el tipo de contenido como "application/octet-stream"
    response['Content-Disposition'] = f'attachment; filename="{archivo_documento.name}"'

    return response