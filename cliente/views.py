from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from index.forms import *
from django.contrib import messages
from index.models import Cliente
from django.db import transaction
from django.core.mail import send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import mimetypes
from django.contrib.auth.decorators import login_required, user_passes_test

#Gestión Clientes
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def regcliente(request):
    data = {
        'form': ClienteForm()
    }

    if request.method == "POST":
        formulario = ClienteForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            #data['mensaje'] = "Se ha guardado el cliente correctamente"
            return redirect("Lista Cliente")
    return render(request, "cliente/regcliente.html", data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def editarcliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    data = {'form': ClienteForm(instance=cliente)}

    if request.method == 'POST':
        formulario = ClienteForm(data=request.POST, instance=cliente)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Modificado correctamente")
            return redirect('Lista Cliente')
        else:
            messages.error(request, "Error al modificar el cliente. Por favor, corrige los errores en el formulario.")

    return render(request, 'cliente/editarcliente.html', data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def listacliente(request):
    clientes = Cliente.objects.all()
    data = {
        'cliente': clientes
    }
    return render(request, "cliente/listacliente.html", data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def eliminar_cliente(request, cliente_id):
    cliente = Cliente.objects.get(id=cliente_id)
    
    # Verificar si el cliente existe
    if cliente:
        # Eliminar al cliente
        cliente.delete()
        messages.success(request, 'El cliente se eliminó correctamente.')
    else:
        messages.error(request, 'No se encontró el cliente especificado.')
    
    return redirect('Lista Cliente')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def seleccionar_cliente(request,cliente_id):
    # Obtener el cliente seleccionado
    cliente_select = Cliente.objects.get(id=cliente_id)
    # Guardar la dirección seleccionada en la sesión
    request.session['cliente_select'] = cliente_select.id
    # Redirigir a la vista para ver la dirección seleccionada
    return redirect('Perfil')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def perfilcliente(request):
    cliente = Cliente.objects.get(id=request.session['cliente_select'])
    cotizaciones = Cotizacion.objects.filter(cliente=cliente)
    ventas = Venta.objects.filter(cotizacion__in=cotizaciones)
    context = {
        "cliente" : cliente,
        "cotizaciones" : cotizaciones,
        "ventas" : ventas
    }

    return render(request, 'cliente/perfil.html', context)

#Gestión Cotizacion
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def seleccionar_servicios(request):
    servicio = Servicio.objects.all()
    data = {
        'servicio': servicio
    }
    return render(request, "cliente/selectserv.html", data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def crear_cotizacion(request):
    
    if request.method == 'POST':
        with transaction.atomic():
            # Crear una nueva instancia de Cotizacion
            cliente = Cliente.objects.get(id=request.session['cliente_select'])
            cotizacion = Cotizacion( venta=False,cliente_id = request.session['cliente_select'])
            cotizacion.descuento = request.POST.get(f'descuento')
            cotizacion.save()
            # Sumar contador de cotizacion
            cliente.cont_cotizacion = cliente.cont_cotizacion+1
            cliente.save()
            for servicio in Servicio.objects.all():
                cantidad = request.POST.get(f'cantidad_{servicio.id}')
                descuento = request.POST.get(f'descuento_{servicio.id}')

                detalle_cotizacion = DetalleCotizacion(
                    cantidad=int(cantidad),
                    descuento=int(descuento),
                    servicio=servicio,
                    cotizacion=cotizacion
                )
                detalle_cotizacion.save()
    
        return redirect('Perfil')  # Redirigir a la página deseada después de procesar el formulario

    return render(request, 'selectserv.html')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def editarcotizacion(request, id):
    servicio = Servicio.objects.all()
    cotizacion = Cotizacion.objects.get(id=id)
    detalle_cotizacion = DetalleCotizacion.objects.filter(cotizacion=cotizacion)
    if request.method == 'POST':
        for servicio in Servicio.objects.all():
            cantidad = request.POST.get(f'cantidad_{servicio.id}')
            descuento = request.POST.get(f'descuento_{servicio.id}')
            detalle_existente = detalle_cotizacion.filter(servicio=servicio).first()

            if detalle_existente:
                if cantidad is not None:
                    detalle_existente.cantidad = int(cantidad)
                if descuento is not None:
                    detalle_existente.descuento = int(descuento)
                detalle_existente.save()
            else:
                detalle_nuevo = DetalleCotizacion(
                    cantidad=0,
                    descuento=0,
                    servicio=servicio,
                    cotizacion=cotizacion
                )
                detalle_nuevo.save()

        cotizacion.descuento = request.POST.get(f'descuento2')
        cotizacion.save()

        return redirect('Perfil')

    data = {
        'servicio': servicio,
        'cotizacion': cotizacion,
        'detalle': detalle_cotizacion
    }
    return render(request, "cliente/editarcotizacion.html", data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def ver_cotizacion(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    subtotal = 0
    descuentos = 0
    total = 0
    descuentos_porcentaje = 0.0
    detalle_cotizacion = DetalleCotizacion.objects.filter(cotizacion=cotizacion, cantidad__gt=0)
    
    for d in detalle_cotizacion:
        subtotal = subtotal + d.subtotal()
        descuentos = descuentos + d.descuentos()
        
    descuentos = descuentos + cotizacion.descuento
    
    if subtotal != 0:
        descuentos_porcentaje = (descuentos * 100) / subtotal
    else:
        descuentos_porcentaje = 0.0
        
    descuentos_porcentaje = round(descuentos_porcentaje, 1)
    total = subtotal - descuentos
    
    data = {
        'cotizacion': cotizacion,
        'detalle': detalle_cotizacion,
        'subtotal': subtotal,
        'descuentos': descuentos,
        'total': total,
        'descuentos_porcentaje': descuentos_porcentaje
    }
    
    return render(request, "cliente/cotizacion.html", data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def aceptar_cotizacion(request,id):
    cotizacion = Cotizacion.objects.get(id=id)
    cotizacion.aceptado = True
    cotizacion.abierta = True
    cotizacion.save()
    
    #total a venta
    subtotal = 0
    descuentos = 0
    total = 0
    detalle_cotizacion = DetalleCotizacion.objects.filter(cotizacion=cotizacion, cantidad__gt=0)
    for d in detalle_cotizacion:
        subtotal = subtotal + d.subtotal()
        descuentos = descuentos + d.descuentos()
    descuentos = descuentos + cotizacion.descuento
    total = subtotal - descuentos
    
    #Crear instancia Venta
    venta = Venta.objects.create(cotizacion=cotizacion)
    venta.total = total
    venta.deuda = total
    venta.save()
    
    # Restar contador de cotizacion
    cliente = Cliente.objects.get(id=request.session['cliente_select'])
    cliente.cont_cotizacion = cliente.cont_cotizacion-1
    # Sumar contador de Venta abierta
    cliente.cont_ventaA = cliente.cont_ventaA+1


    cliente.save()

    
    return redirect('Perfil')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def rechazar_cotizacion(request,id):
    
    cotizacion = Cotizacion.objects.get(id=id)
    cotizacion.rechazado = True
    cotizacion.save()
    
    # Restar contador de cotizacion
    cliente = Cliente.objects.get(id=request.session['cliente_select'])
    cliente.cont_cotizacion = cliente.cont_cotizacion-1
    cliente.save()
    
    return redirect('Perfil')


#envio cotización
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def enviar_correo(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    subtotal = 0
    descuentos = 0
    total = 0
    descuentos_porcentaje = 0.0
    detalle_cotizacion = DetalleCotizacion.objects.filter(cotizacion=cotizacion, cantidad__gt=0)
    for d in detalle_cotizacion:
        subtotal += d.subtotal()
        descuentos += d.descuentos()
        
    descuentos += cotizacion.descuento
    
    descuentos_porcentaje = (descuentos * 100) / subtotal
    descuentos_porcentaje = round(descuentos_porcentaje, 1)
    total = subtotal - descuentos
    data = {
        'cotizacion': cotizacion,
        'detalle': detalle_cotizacion,
        'subtotal': subtotal,
        'descuentos': descuentos,
        'total': total,
        'descuentos_porcentaje': descuentos_porcentaje
    }

    cliente_id = request.session['cliente_select']
    cliente = Cliente.objects.get(id=cliente_id)

    # Obtener el nombre y el correo del cliente
    nombre_cliente = cliente.nombre
    correo_cliente = cliente.correo

    # Configurar el asunto del correo
    asunto = "Gracias por realizar tu cotización"

    # Obtener el contenido del mensaje en HTML
    mensaje_html = render_to_string("cliente/enviomail.html", {
        "nombre_cliente": nombre_cliente,
        "cotizacion": cotizacion,
        "detalle": detalle_cotizacion,
        "subtotal": subtotal,
        "descuentos": descuentos,
        "total": total,
        "descuentos_porcentaje": descuentos_porcentaje
    })

    # Configurar los datos del correo electrónico
    from_email = "keyspandacl@gmail.com"
    to = correo_cliente

    # Enviar el correo electrónico
    send_mail(asunto, "", from_email, [to], html_message=mensaje_html)
    cotizacion.email_enviado = True
    cotizacion.save()

    # Renderizar la plantilla y generar la respuesta HTTP
    return redirect('Perfil')

#Envio de encuesta
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def enviar_encuesta(request, id):
    cliente = Cliente.objects.get(id=request.session['cliente_select'])
    venta = Venta.objects.get(id=id)
    # Obtener el nombre y el correo del cliente
    nombre_cliente = cliente.nombre
    correo_cliente = cliente.correo

    # Configurar el asunto del correo
    asunto = "Por favor, Califica tu experiencia con InnovaPIE"

    # Obtener el contenido del mensaje en HTML
    mensaje_html = render_to_string("cliente/encuesta.html", {
        "nombre_cliente": nombre_cliente,
    })

    # Configurar los datos del correo electrónico
    from_email = "keyspandacl@gmail.com"
    to = correo_cliente

    # Enviar el correo electrónico
    send_mail(asunto, "", from_email, [to], html_message=mensaje_html)
    venta.estado_encuesta = True
    venta.save()

    return redirect('Perfil')

#Ventas
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def ver_venta(request,id):
    cliente = Cliente.objects.get(id=request.session['cliente_select'])
    venta = Venta.objects.get(id=id)
    pagos = Pago.objects.filter(venta=venta)
    facturas =  Factura.objects.filter(venta=venta)
    
    detalle_cotizacion = DetalleCotizacion.objects.filter(cotizacion=venta.cotizacion, cantidad__gt=0)
    
    subtotal = sum(d.subtotal() for d in detalle_cotizacion)
    descuento = sum(d.descuentos() for d in detalle_cotizacion)
    pagos2 = sum(p.total for p in pagos)
    venta.total = subtotal - (descuento + venta.cotizacion.descuento)
    venta.deuda = (subtotal - (descuento + venta.cotizacion.descuento))-pagos2
    venta.save()
    
    data = {
        "cliente" : cliente,
        "venta" : venta,
        "pagos" : pagos,
        "facturas" : facturas
    }
    return render(request, "cliente/venta.html",data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def ver_venta_cerrada(request,id):
    cliente = Cliente.objects.get(id=request.session['cliente_select'])
    venta = Venta.objects.get(id=id)
    pagos = Pago.objects.filter(venta=venta)
    facturas =  Factura.objects.filter(venta=venta)
    
    detalle_cotizacion = DetalleCotizacion.objects.filter(cotizacion=venta.cotizacion, cantidad__gt=0)
    
    subtotal = sum(d.subtotal() for d in detalle_cotizacion)
    descuento = sum(d.descuentos() for d in detalle_cotizacion)
    pagos2 = sum(p.total for p in pagos)
    venta.total = subtotal - (descuento + venta.cotizacion.descuento)
    venta.deuda = (subtotal - (descuento + venta.cotizacion.descuento))-pagos2
    venta.save()
    
    data = {
        "cliente" : cliente,
        "venta" : venta,
        "pagos" : pagos,
        "facturas" : facturas
    }
    return render(request, "cliente/ver_venta_cerrada.html",data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def cerrar_venta(request,id):
    venta = Venta.objects.get(id=id)
    #Pasar a Venta Cerrada
    venta.cerrada = True
    venta.abierta = False
    venta.save()
    venta.cotizacion.abierta = False
    venta.cotizacion.cerrada = True
    venta.cotizacion.save()
    #Descontar venta abierta
    venta.cotizacion.cliente.cont_ventaA = venta.cotizacion.cliente.cont_ventaA - 1
    venta.cotizacion.cliente.save()
    #Sumar venta Cerrada
    venta.cotizacion.cliente.cont_ventaC = venta.cotizacion.cliente.cont_ventaC + 1
    venta.cotizacion.cliente.save()
    
    return redirect('Perfil')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def editar_venta(request, id):
    try:
        venta = Venta.objects.get(id=id)
    except Venta.DoesNotExist:
        # Manejar el caso en que no se encuentre la venta
        # Puedes redirigir a una página de error o realizar alguna acción apropiada
        return HttpResponse("La venta no existe")

    detalle_cotizacion = DetalleCotizacion.objects.filter(cotizacion=venta.cotizacion)
    pagos = int(venta.total) - int(venta.deuda)

    if request.method == 'POST':
        for servicio in Servicio.objects.all():
            cantidad = request.POST.get(f'cantidad_{servicio.id}')
            descuento = request.POST.get(f'descuento_{servicio.id}')
            detalle_existente = detalle_cotizacion.filter(servicio=servicio).first()

            if detalle_existente:
                if cantidad is not None:
                    detalle_existente.cantidad = int(cantidad)
                if descuento is not None:
                    detalle_existente.descuento = int(descuento)
                detalle_existente.save()
            else:
                detalle_nuevo = DetalleCotizacion(
                    cantidad=0,
                    descuento=0,
                    servicio=servicio,
                    cotizacion=venta.cotizacion
                )
                detalle_nuevo.save()

        descuento2 = request.POST.get(f'descuento2')
        venta.cotizacion.descuento = int(descuento2) if descuento2 is not None else 0
        venta.cotizacion.save()

        return redirect('Perfil')

    servicio = Servicio.objects.all()
    data = {
        'servicio': servicio,
        'venta': venta,
        'cotizacion': venta.cotizacion,
        'detalle': detalle_cotizacion
    }
    return render(request, "cliente/editarventa.html", data)

#Pago
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def nuevo_pago(request, id):
    venta = Venta.objects.get(id=id)

    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        total = request.POST.get('total')
        
        pago = Pago(venta=venta, archivo=archivo, total=total)
        pago.save()
        #Restar deuda
        venta.deuda = venta.deuda - int(total)
        venta.save()
        
        return redirect('Venta', id=id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())    
def descargar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)

    # Realiza cualquier lógica adicional necesaria, como verificar permisos, etc.

    # Obtén el archivo de la factura y su nombre
    archivo_pago = pago.archivo
    nombre_factura = pago.archivo

    # Crea una respuesta HTTP con el archivo adjunto
    response = HttpResponse(archivo_pago, content_type='image/png')  # Establece el tipo de contenido como "image/png"
    response['Content-Disposition'] = f'attachment; filename="{nombre_factura}"'

    return response

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def eliminar_pago(request,id):
    pago = Pago.objects.get(id=id)
    venta = Venta.objects.get(id=pago.venta.id)
    # Verificar si el cliente existe
    if pago:
        # Sumar deuda
        venta.deuda = venta.deuda + pago.total
        venta.save()
        # Eliminar al cliente
        pago.delete()
        messages.success(request, 'El pago se eliminó correctamente.')
    else:
        messages.error(request, 'No se encontró el pago especificado.')
    
    return redirect('Venta', id= venta.id)

#Factura
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def nueva_factura(request, id):
    venta = Venta.objects.get(id=id)

    if request.method == 'POST':
        numero_factura = request.POST.get('numero_factura')
        archivo = request.FILES.get('archivo')
        total = request.POST.get('total')
        fecha = request.POST.get('fecha')
        
        factura = Factura(venta=venta,numero_factura=numero_factura , archivo=archivo, total=total, fecha=fecha)
        factura.save()
        
        return redirect('Venta', id=id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def descargar_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)

    # Realiza cualquier lógica adicional necesaria, como verificar permisos, etc.

    # Obtén el archivo de la factura y su nombre
    archivo_factura = factura.archivo
    nombre_factura = factura.archivo

    # Crea una respuesta HTTP con el archivo adjunto
    response = HttpResponse(archivo_factura, content_type='image/png')  # Establece el tipo de contenido como "image/png"
    response['Content-Disposition'] = f'attachment; filename="{nombre_factura}"'

    return response

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def eliminar_factura(request,id):
    factura = Factura.objects.get(id=id)
    venta = Venta.objects.get(id=factura.venta.id)
    # Verificar si el cliente existe
    if factura:
        # Eliminar al cliente
        factura.delete()
        messages.success(request, 'La Factura se eliminó correctamente.')
    else:
        messages.error(request, 'No se encontró la factura especificada.')
    
    return redirect('Venta', id= venta.id)

#Envio de factura
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def enviar_factura(request, id):
    factura = Factura.objects.get(id=id)
    cliente = factura.venta.cotizacion.cliente
    venta = factura.venta

    # Obtener el nombre y el correo del cliente
    nombre_cliente = cliente.nombre
    correo_cliente = cliente.correo

    # Configurar el asunto del correo
    asunto = "Envio factura de venta con InnovaPIE"

    # Obtener el contenido del mensaje en HTML
    mensaje_html = render_to_string("cliente/mailadjunto.html", {
        "nombre_cliente": nombre_cliente,
    })

    # Configurar los datos del correo electrónico
    from_email = "keyspandacl@gmail.com"
    to = correo_cliente

    # Obtener el archivo adjunto
    factura = get_object_or_404(Factura, id=id)
    adjunto = factura.archivo

    # Crear el objeto EmailMessage sin agregar el archivo adjunto por ahora
    email = EmailMessage(
        subject=asunto,
        body=mensaje_html,
        from_email=from_email,
        to=[to],
    )

    # Verificar si el archivo adjunto existe antes de intentar adjuntarlo
    if adjunto:
        # Obtener el nombre del archivo original
        file_name = adjunto.name.split("/")[-1]  # Extract the filename from the full path

        # Obtener la ruta del archivo
        archivo_path = adjunto.file.name
        # Abrir el archivo
        with open(archivo_path, "rb") as f:
            # Leer el contenido del archivo
            adjunto_data = f.read()

        # Obtener el tipo de contenido del archivo basado en su extensión
        content_type, encoding = mimetypes.guess_type(archivo_path)
        # Si no se puede determinar el tipo de contenido, establecer un valor predeterminado
        if not content_type:
            content_type = "application/octet-stream"

        # Adjuntar el archivo al mensaje de correo electrónico con su nombre original
        email.attach(file_name, adjunto_data, "text/html")  # Especificar "text/html" como el tipo de contenido

    # Enviar el correo electrónico
    email.send()
    factura.factura_enviada = True
    factura.save()


    return redirect('Venta', id = venta.id)

