
from django.urls import path
from cliente import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    #Clientes
    path('', views.listacliente, name="Lista Cliente"),
    path('registrocliente/', views.regcliente, name="Registro Cliente"),
    path('eliminar_cliente/<int:cliente_id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('editarcliente/<id>/', views.editarcliente, name='editar_cliente'),
    #Cotizaciones
    path('seleccionarservicio', views.seleccionar_servicios, name="Select Serv"),
    path('perfil/', views.perfilcliente, name="Perfil"),
    path('seleccionar/<int:cliente_id>/', views.seleccionar_cliente, name="seleccionar_cliente"),
    path('crear_cotizacion/', views.crear_cotizacion, name='crear_cotizacion'),
    path('editarcotizacion/<id>/', views.editarcotizacion, name='editar_cotizacion'),
    path('perfil/cotizacion/<id>/', views.ver_cotizacion, name="ver_cotizacion"),
    path('perfil/venta/cotizacion/<id>/', views.ver_cotizacion, name="ver_venta"),

    #aceptar o rechazar
    path('perfil/aceptar/<int:id>/', views.aceptar_cotizacion, name="aceptar_cotizacion"),
    path('perfil/rechazar/<int:id>/', views.rechazar_cotizacion, name="rechazar_cotizacion"),
    path('cliente/perfil/enviar_mail/<id>/', views.enviar_correo, name="enviar_correo"),
    path('cliente/perfil/enviar_encuesta/<id>/', views.enviar_encuesta, name="enviar_encuesta"),
    path('perfil/venta/enviar_factura/<id>/', views.enviar_factura, name="enviar_factura"),
    #Urls de ventas
    path('perfil/venta/<id>/', views.ver_venta, name="Venta"),  
    path('perfil/ventacerrada/<id>/', views.ver_venta_cerrada, name="Venta_cerrada"),   
    path('perfil/cerrar_venta/<id>/', views.cerrar_venta, name="cerrar_venta"),
    path('perfil/editar_venta/<id>/', views.editar_venta, name='editar_venta'),
    #Urls de facturas
    path('perfil/venta/factura/<id>', views.nueva_factura, name="nueva_factura"),
    path('eliminar_factura/<id>/', views.eliminar_factura, name='eliminar_factura'),
    path('perfil/venta/descargar-factura/<int:factura_id>/', views.descargar_factura, name='descargar_factura'),
    #Urls de Pagos   
    path('perfil/venta/pago/<id>', views.nuevo_pago, name="nuevo_pago"),
    path('eliminar_pago/<id>/', views.eliminar_pago, name='eliminar_pago'),
    path('perfil/venta/descargar-pago/<int:pago_id>/', views.descargar_pago, name='descargar_pago'),


    
    

]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)