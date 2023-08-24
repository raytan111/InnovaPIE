import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from index.models import Factura, Pago, Boleta_Honorario,Costos_fijos,Costos_variables, PerfilUsuario
from .forms import MonthYearForm
import calendar
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.figure as mfig
import matplotlib.backends.backend_agg as agg
from django.db.models import Q, Sum, Value
from datetime import datetime, timedelta
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages




@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def venta(request):
    return render(request, "venta/ventas.html")

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def ingreso2(request):
    # Inicialización de totales
    totalfacturas = 0
    totalpagos = 0
    ingresostotal = 0
    
    # Si el método es POST, obtenemos la fecha desde el formulario
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
    # Si el método es GET, establecemos la fecha actual como valor por defecto
    else:
        fecha_str = datetime.now().strftime('%Y-%m')

    # Convertimos la fecha_str a un objeto datetime
    fecha = datetime.strptime(fecha_str, "%Y-%m")

    # Filtramos los registros según la fecha
    facturas = Factura.objects.filter(Q(fecha__year=fecha.year) & Q(fecha__month=fecha.month))
    pagos = Pago.objects.filter(Q(fecha_hora__year=fecha.year) & Q(fecha_hora__month=fecha.month))
    
    for f in facturas: 
        totalfacturas += f.total

    for p in pagos: 
        totalpagos += p.total

    ingresostotal = totalfacturas + totalpagos

    data = {
        "facturas" : facturas,
        "pagos" : pagos,
        "fecha_str" : fecha_str,
        "total_factura" : totalfacturas,
        "total_pago" : totalpagos,
        "total" : ingresostotal,
    }

    return render(request, "venta/ingresos2.html", data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def egreso2(request):
    colaboradores = PerfilUsuario.objects.all()
    
    # Inicialización de totales
    totalboletas = 0
    totalfijo = 0
    totalvariable = 0
    totalegreso = 0

    # Si el método es POST, obtenemos la fecha desde el formulario
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
    # Si el método es GET, establecemos la fecha actual como valor por defecto
    else:
        fecha_str = datetime.now().strftime('%Y-%m')

    # Convertimos la fecha_str a un objeto datetime
    fecha = datetime.strptime(fecha_str, "%Y-%m")

    # Filtramos los registros según la fecha
    boletas = Boleta_Honorario.objects.filter(Q(fecha__year=fecha.year) & Q(fecha__month=fecha.month))
    fijos = Costos_fijos.objects.filter(Q(fecha__year=fecha.year) & Q(fecha__month=fecha.month))
    variables = Costos_variables.objects.filter(Q(fecha__year=fecha.year) & Q(fecha__month=fecha.month))
    
    for b in boletas: 
        totalboletas += b.total

    for f in fijos: 
        totalfijo += f.total

    for v in variables: 
        totalvariable += v.total

    totalegreso = totalboletas + totalfijo + totalvariable

    data = {
        "fecha_str" : fecha_str,
        "boletas" : boletas,
        "fijos" : fijos,
        "variables" : variables,
        "total_boletas" : totalboletas,
        "total_fijo" : totalfijo,
        "total_variable" : totalvariable,
        "total" : totalegreso,
        "colaboradores" : colaboradores,
    }

    return render(request, "venta/egresos2.html", data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def reporte(request):
    pagos = Pago.objects.all()

    return render(request, "venta/reportes.html")

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def tabla1(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido."}, status=405)

    fecha_inicio_str = request.POST.get('fecha_inicio')
    fecha_fin_str = request.POST.get('fecha_fin')

    if not fecha_inicio_str or not fecha_fin_str:
        return JsonResponse({"error": "Fechas no proporcionadas."}, status=400)

    fecha_inicio = timezone.make_aware(datetime.strptime(fecha_inicio_str, "%Y-%m-%d"))
    fecha_fin = timezone.make_aware(datetime.strptime(fecha_fin_str, "%Y-%m-%d"))

    results = []

    current_month = fecha_inicio
    while current_month <= fecha_fin:
        # Calcula las fechas de inicio y fin para el mes actual
        start_month = current_month
        end_month = start_month + relativedelta(months=1) - relativedelta(days=1)

        # Ingresos
        totalpagos = sum(p.total for p in Pago.objects.filter(fecha_hora__range=(start_month, end_month)))

        # Egresos
        totalboletas = sum(b.total for b in Boleta_Honorario.objects.filter(fecha__range=(start_month, end_month))) 
        totalfijo = sum(f.total for f in Costos_fijos.objects.filter(fecha__range=(start_month, end_month)))
        totalvariable = sum(v.total for v in Costos_variables.objects.filter(fecha__range=(start_month, end_month)))

        totalegreso = totalboletas + totalfijo + totalvariable
        diferencia = totalpagos - totalegreso

        # Agrega el resultado a la lista
        results.append({
            "fecha_inicio_str": start_month.strftime("%Y-%m-%d"),
            "fecha_fin_str": end_month.strftime("%Y-%m-%d"),
            "total_ingreso": totalpagos,
            "total_egreso": totalegreso,
            "diferencia": diferencia,
        })

        # Avanza al siguiente mes
        current_month += relativedelta(months=1)

    data = {
        "results": results
    }

    return JsonResponse(data)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def produccion_tabla(request):
    if request.method == 'GET':
        fecha_inicio_str = request.GET.get('fecha_inicio')
        fecha_fin_str = request.GET.get('fecha_fin')
        fecha_inicio = timezone.make_aware(datetime.strptime(fecha_inicio_str, "%Y-%m-%d"))
        fecha_fin_temp = datetime.strptime(fecha_fin_str, "%Y-%m-%d")
        fecha_fin = timezone.make_aware(fecha_fin_temp + relativedelta(months=1) - relativedelta(days=1))

        searchText = request.GET.get('search', "")  # Obtener el texto de búsqueda

        # Si hay texto de búsqueda, filtrar por nombre, apellido o profesión
        if searchText:
            perfiles = PerfilUsuario.objects.filter(
                Q(nombre__icontains=searchText) | 
                Q(apellidop__icontains=searchText) |
                Q(profesion__icontains=searchText)
            )
        else:
            perfiles = PerfilUsuario.objects.all()

        data = []

        for perfil in perfiles:
            boletas = Boleta_Honorario.objects.filter(
                colaborador=perfil,
                fecha__range=(fecha_inicio, fecha_fin)
            )

            total_ingresos = boletas.aggregate(total=Coalesce(Sum('total'), Value(0)))['total']
            total_evaluaciones = boletas.aggregate(total_evaluaciones=Coalesce(Sum('cantidad_evaluaciones'), Value(0)))['total_evaluaciones']

            data.append({
                'nombre': perfil.nombre,
                'apellido': perfil.apellidop,  # Ajustar según cómo quieras mostrar el apellido
                'profesion': perfil.profesion,
                'total_ingresos': total_ingresos,
                'total_evaluaciones': total_evaluaciones
            })

        return JsonResponse({'data': data})

    # Si no es GET, devolvemos un error.
    return HttpResponseBadRequest("Método no permitido")

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def ingresos_egresos_mes(request):
    if request.method == 'POST':
        # Fecha
        fecha_str = request.POST.get('fecha')
        fecha = datetime.strptime(fecha_str, "%Y")
        
        # Ingresos
        pagos = Pago.objects.filter(Q(fecha_hora__year=fecha.year))
        # Egresos
        boletas = Boleta_Honorario.objects.filter(Q(fecha__year=fecha.year))
        fijos = Costos_fijos.objects.filter(Q(fecha__year=fecha.year))
        variables = Costos_variables.objects.filter(Q(fecha__year=fecha.year))
        
        # Crear un diccionario para almacenar los ingresos por mes
        ingresos_por_mes = defaultdict(float)
        
        # Calcular los ingresos por mes
        for pago in pagos:
            mes = pago.fecha_hora.month
            ingresos_por_mes[mes] += pago.total
        
        # Crear un diccionario para almacenar los egresos por mes
        egresos_por_mes = defaultdict(float)

        # Calcular los egresos por mes
        for boleta in boletas:
            mes = boleta.fecha.month
            egresos_por_mes[mes] += boleta.total

        for fijo in fijos:
            mes = fijo.fecha.month
            egresos_por_mes[mes] += fijo.total

        for variable in variables:
            mes = variable.fecha.month
            egresos_por_mes[mes] += variable.total
        
        # Convertir los datos en listas para el gráfico
        meses = list(range(1, 13))
        ingresos = [ingresos_por_mes[mes] for mes in meses]
        egresos = [egresos_por_mes[mes] for mes in meses]
        
        # Crear un gráfico de barras usando la API orientada a objetos
        fig = mfig.Figure()
        ax = fig.add_subplot(111)

        # Ajustar la posición de las barras para que no se superpongan
        bar_width = 0.35
        ax.bar([mes - bar_width/2 for mes in meses], ingresos, bar_width, color='#72B62F', label='Ingresos')
        ax.bar([mes + bar_width/2 for mes in meses], egresos, bar_width, color='#BD1521', label='Egresos')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Monto')
        ax.set_title('Ingresos y Egresos por Mes en {}'.format(fecha.year))
        ax.set_xticks(meses)
        ax.set_xticklabels(calendar.month_abbr[1:])
        ax.legend()
        
        # Guardar el gráfico en un buffer
        buffer = BytesIO()
        canvas = agg.FigureCanvasAgg(fig)
        canvas.print_figure(buffer, format='png')
        
        # Guardar el gráfico en un directorio temporal
        image_filename = "temp_chart_{}.png".format(fecha.year)
        image_path = os.path.join(settings.MEDIA_ROOT, image_filename)
        canvas.print_figure(image_path, format='png')
        
        # Devolver URL de la imagen en lugar de la imagen directamente
        response_data = {
            "image_url": os.path.join(settings.MEDIA_URL, image_filename)
        }
        return JsonResponse(response_data)
    
    return redirect('reporte')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def ingresos_egresos_ano(request):
    if request.method == 'POST':
        # Seleccionar los últimos 5 años
        today = datetime.now()
        year_range = range(today.year - 4, today.year + 1)
        
        # Crear un diccionario para almacenar los ingresos y egresos por año
        ingresos_por_ano = defaultdict(float)
        egresos_por_ano = defaultdict(float)
        
        # Calcular los ingresos y egresos por año
        for year in year_range:
            pagos_anuales = Pago.objects.filter(fecha_hora__year=year)
            ingresos_por_ano[year] = sum(pago.total for pago in pagos_anuales)
            
            boletas_anuales = Boleta_Honorario.objects.filter(fecha__year=year)
            fijos_anuales = Costos_fijos.objects.filter(fecha__year=year)
            variables_anuales = Costos_variables.objects.filter(fecha__year=year)
            egresos_por_ano[year] = sum(boleta.total for boleta in boletas_anuales) + \
                                    sum(fijo.total for fijo in fijos_anuales) + \
                                    sum(variable.total for variable in variables_anuales)

        # Convertir los datos en listas para el gráfico
        years = list(year_range)
        ingresos = [ingresos_por_ano[year] for year in years]
        egresos = [egresos_por_ano[year] for year in years]
        
        # Crear un gráfico de barras usando la API orientada a objetos
        fig = mfig.Figure()
        ax = fig.add_subplot(111)
        
        bar_width = 0.35
        ax.bar([year - bar_width/2 for year in years], ingresos, bar_width, color='#72B62F', label='Ingresos')
        ax.bar([year + bar_width/2 for year in years], egresos, bar_width, color='#BA4A00', label='Egresos')
        ax.set_xlabel('Año')
        ax.set_ylabel('Monto')
        ax.set_title('Ingresos y Egresos por Año en los últimos 5 años')
        ax.set_xticks(years)
        ax.legend()

        # Guardar el gráfico en un buffer
        buffer = BytesIO()
        canvas = agg.FigureCanvasAgg(fig)
        canvas.print_figure(buffer, format='png')

        # Guardar el gráfico en un directorio temporal
        image_filename = "temp_chart.png"
        image_path = os.path.join(settings.MEDIA_ROOT, image_filename)
        with open(image_path, 'wb') as f:
            f.write(buffer.getvalue())

        # Devolver URL de la imagen en lugar de la imagen directamente
        response_data = {
            "image_url": os.path.join(settings.MEDIA_URL, image_filename)
        }
        
        return JsonResponse(response_data)
    
    return redirect('reporte')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def nuevo_costo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        fecha = request.POST.get('fecha')
        archivo = request.FILES.get('archivo')
        impuesto = request.POST.get('impuesto')
        total = request.POST.get('total')

        costo = Costos_fijos(nombre=nombre, fecha=fecha, archivo=archivo, impuesto=impuesto, total=total)
        costo.save()

        return JsonResponse({'status': 'ok'}, status=200)
    else:
        return JsonResponse({'status': 'bad request'}, status=400)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())    
def nuevo_costo_variable(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        fecha = request.POST.get('fecha')
        archivo = request.FILES.get('archivo')
        impuesto = request.POST.get('impuesto')
        total = request.POST.get('total')

        costo = Costos_variables(nombre=nombre, fecha=fecha, archivo=archivo, impuesto=impuesto, total=total)
        costo.save()

        return JsonResponse({'status': 'ok'}, status=200)
    else:
        return JsonResponse({'status': 'bad request'}, status=400)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def nueva_boleta(request):
    if request.method == 'POST':
        numero = request.POST.get('numero')
        archivo = request.FILES.get('archivo')
        total = request.POST.get('total')
        cantidad_evaluaciones = request.POST.get('cantidad_evaluaciones')
        retencion = request.POST.get('retencion')
        fecha = request.POST.get('fecha')
        colaborador_id = request.POST.get('colaborador')

        try:
            colaborador = PerfilUsuario.objects.get(id=colaborador_id)
        except PerfilUsuario.DoesNotExist:
            return JsonResponse({'status': 'bad request', 'error': 'Colaborador no existe'}, status=400)

        boleta = Boleta_Honorario(numero=numero, archivo=archivo, total=total, 
                                  cantidad_evaluaciones=cantidad_evaluaciones, 
                                  retencion=retencion, fecha=fecha, colaborador=colaborador)
        boleta.save()

        return JsonResponse({'status': 'ok'}, status=200)
    else:
        return JsonResponse({'status': 'bad request'}, status=400)
    

#descargar archivos
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def descargar_archivo_costo_variable(request, variable_id):
    costo_variable = get_object_or_404(Costos_variables, id=variable_id)

    # Obtener el archivo y su nombre
    archivo = costo_variable.archivo
    nombre_archivo = archivo.name.split('/')[-1]

    # Crear una respuesta HTTP con el archivo adjunto
    response = HttpResponse(archivo, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    return response

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def descargar_archivo_costo_fijo(request, fijo_id):
    costo_fijo = get_object_or_404(Costos_fijos, id=fijo_id)

    # Obtener el archivo y su nombre
    archivo = costo_fijo.archivo
    nombre_archivo = archivo.name.split('/')[-1]

    # Crear una respuesta HTTP con el archivo adjunto
    response = HttpResponse(archivo, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    return response

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def descargar_boleta_honorario(request, boleta_id):
    boleta = get_object_or_404(Boleta_Honorario, id=boleta_id)

    # Obtener el archivo y su nombre
    archivo = boleta.archivo
    nombre_archivo = archivo.name.split('/')[-1]

    # Crear una respuesta HTTP con el archivo adjunto
    response = HttpResponse(archivo, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    return response

#Botones eliminar Costos
@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def eliminar_variable(request,id):
    variables = Costos_variables.objects.get(id=id)
    
    # Verificar si el cliente existe
    if variables:
        # Eliminar al cliente
        variables.delete()
        messages.success(request, 'El Egreso se eliminó correctamente.')
    else:
        messages.error(request, 'No se encontró el Egreso especificado.')
    
    return redirect('egresof')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def eliminar_fijo(request,id):
    fijos = Costos_fijos.objects.get(id=id)
    
    # Verificar si el cliente existe
    if fijos:
        # Eliminar al cliente
        fijos.delete()
        messages.success(request, 'El Egreso se eliminó correctamente.')
    else:
        messages.error(request, 'No se encontró el Egreso especificado.')
    
    return redirect('egresof')

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Administrador').exists())
def eliminar_boleta(request,id):
    boletas = Boleta_Honorario.objects.get(id=id)
    
    # Verificar si el cliente existe
    if boletas:
        # Eliminar al cliente
        boletas.delete()
        messages.success(request, 'El Egreso se eliminó correctamente.')
    else:
        messages.error(request, 'No se encontró el Egreso especificado.')
    
    return redirect('egresof')