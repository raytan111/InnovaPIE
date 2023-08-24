from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Cliente)
admin.site.register(Servicio)
admin.site.register(Cotizacion)
admin.site.register(DetalleCotizacion)
admin.site.register(Venta)
admin.site.register(Pago)
admin.site.register(Factura)
admin.site.register(PerfilUsuario)
admin.site.register(Documento)
admin.site.register(Boleta_Honorario)
admin.site.register(Costos_fijos)
admin.site.register(Costos_variables)
admin.site.register(DatosTransferencia)

