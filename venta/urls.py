
from django.urls import path
from venta import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.venta, name='venta'),
    path('ingresosf/', views.ingreso2, name='ingresof'),
    path('egresosf/', views.egreso2, name='egresof'),
    path('egresosf/nuevo_costo/', views.nuevo_costo, name='nuevo_costo'),
    path('egresosf/nuevo_costo_variable/', views.nuevo_costo_variable, name='nuevo_costo_variable'),
    path('egresosf/nueva_boleta', views.nueva_boleta, name='nueva_boleta'),
    path('egresosf/variable/<int:variable_id>/', views.descargar_archivo_costo_variable, name='descargar_archivo_costo_variable'),
    path('egresosf/fijo/<int:fijo_id>/', views.descargar_archivo_costo_fijo, name='descargar_archivo_costo_fijo'),
    path('egresosf/boleta/<int:boleta_id>/', views.descargar_boleta_honorario, name='descargar_boleta_honorario'),

    path('egresosf/eliminar_variable/<int:id>/', views.eliminar_variable, name='eliminar_variable'),
    path('egresosf/eliminar_fijo/<int:id>/', views.eliminar_fijo, name='eliminar_fijo'),
    path('egresosf/eliminar_boleta/<int:id>/', views.eliminar_boleta, name='eliminar_boleta'),

    path('reportes/', views.reporte, name='reporte'),
    path('reportes/grafico1/', views.ingresos_egresos_mes, name='grafico1'),
    path('reportes/grafico2/', views.ingresos_egresos_ano, name='grafico2'),

    path('reportes/tabla1/', views.tabla1, name='tabla1'),
    path('reportes/tabla2/', views.produccion_tabla, name='tabla2'),








]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)