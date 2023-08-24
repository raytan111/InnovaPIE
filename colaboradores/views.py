from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from index.forms import NuevoUsuarioForm, PerfilUsuarioForm, DatosTransferenciaForm, EditUsuarioForm
from index.models import PerfilUsuario, DatosTransferencia, Documento
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'colaboradores/lista_usuarios.html', {'usuarios': usuarios})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def listar_colaboradores(request):
    perfil= PerfilUsuario.objects.all()
    return render(request, 'colaboradores/lista_colaboradores.html', {
        'perfil': perfil,
        })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def crear_usuario(request):
    if request.method == 'POST':
        form = NuevoUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()  # Guardar el usuario y obtener el objeto guardado
            perfil = PerfilUsuario.objects.create(usuario=usuario)  # Crear el PerfilUsuario asociado al usuario
            perfil.save()
            datos = DatosTransferencia.objects.create(d_usuario=usuario)
            datos.save()
            return redirect('listar_usuarios')
    else:
        form = NuevoUsuarioForm()
    return render(request, 'colaboradores/registrar_usuario.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def ver_perfil_usuario(request,id):
    usuario = User.objects.get(id=id)
    perfil= get_object_or_404(PerfilUsuario, usuario=usuario)
    datos = DatosTransferencia.objects.get(d_usuario=usuario)
    documentos = Documento.objects.filter(perfil=perfil)

    return render(request, 'colaboradores/perfil_usuario.html', {
        'perfil_usuario': perfil,
        'datos_transferencia': datos,
        'documentos': documentos,
        'usuario': usuario,
    })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def editar_perfil_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    perfil = get_object_or_404(PerfilUsuario, usuario=usuario)
    datos = get_object_or_404(DatosTransferencia, d_usuario=usuario)

    if request.method == 'POST':
        perfil_form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        datos_transferencia_form = DatosTransferenciaForm(request.POST, instance=datos)
        
        if perfil_form.is_valid() and datos_transferencia_form.is_valid():
            perfil_form.save()
            datos_transferencia_form.save()
            return redirect('perfil_usuario', id=id)

    else:
        perfil_form = PerfilUsuarioForm(instance=perfil)
        datos_transferencia_form = DatosTransferenciaForm(instance=datos)

    return render(request, 'colaboradores/editar_usuario.html', {
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
            return redirect('perfilusuario')
        else:
            return render(request, 'error.html', {'mensaje': 'Por favor completa todos los campos del formulario'})

    return render(request, 'colaboradores/nuevo_documento.html', {'perfil_usuario': perfil_usuario})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def eliminar_usuario(request, user_id):
    if request.method == 'POST':
        # Asegúrate de recibir el ID del usuario correctamente
        # Imprime el valor para depurar
        print("ID del usuario a eliminar:", user_id)

        usuario = get_object_or_404(User, id=user_id)
        usuario.delete()

        # Imprime un mensaje para verificar que se eliminó correctamente
        print("Usuario eliminado:", usuario)

        return JsonResponse({'status': 'ok'})

    # Si la solicitud no es POST, podrías redirigir a otra vista o mostrar un mensaje de error
    return JsonResponse({'status': 'error'})



#descargar documento
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


#editar usuario
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def editar_usuario(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        form = EditUsuarioForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = EditUsuarioForm(instance=user)
    return render(request, 'colaboradores/editar_user.html', {'form': form, 'user': user})