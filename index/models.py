from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.IntegerField()
    colegio = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=200)
    comuna = models.CharField(max_length=200)
    tipo_colegio = models.CharField(max_length=200, null=True)
    
    cont_cotizacion = models.IntegerField(default=0)
    cont_ventaA = models.IntegerField(default=0)
    cont_ventaC = models.IntegerField(default=0)
    
    def __str__(self):
        return self.colegio
    
class Servicio(models.Model):
    codigo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=1000)
    precio = models.IntegerField()
    profesional = models.CharField(max_length=100)
    

class Cotizacion(models.Model):
    descuento = models.IntegerField(default=0)
    aceptado = models.BooleanField(default=False)
    rechazado = models.BooleanField(default=False)
    venta = models.BooleanField(default=False)
    email_enviado = models.BooleanField(default=False)
    abierta = models.BooleanField(default=False)
    cerrada = models.BooleanField(default=False)
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    
class DetalleCotizacion(models.Model):
    cantidad = models.IntegerField()
    descuento = models.IntegerField()
    
    servicio = models.ForeignKey(Servicio,on_delete=models.CASCADE)
    cotizacion = models.ForeignKey(Cotizacion,on_delete=models.CASCADE)
    
    def subtotal(self):

        return (self.servicio.precio*self.cantidad)
    
    def descuentos(self):
        return (self.descuento*self.cantidad)
    
    def __str__(self):
        return f"Detalle de cotizacion {self.id}"


class Venta(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True)
    abierta = models.BooleanField(default=True)
    cerrada = models.BooleanField(default=False)
    estado_encuesta = models.BooleanField(default=False)
    total = models.IntegerField(default=0)
    deuda = models.IntegerField(default=0)
    
    cotizacion = models.OneToOneField(Cotizacion, on_delete=models.CASCADE, related_name='ventas')

class Pago(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField()
    total = models.IntegerField()
    
    venta = models.ForeignKey(Venta,on_delete=models.CASCADE)
    
class Factura(models.Model):
    fecha = models.DateField()
    numero_factura = models.IntegerField()
    archivo = models.FileField()
    total = models.IntegerField()
    factura_enviada = models.BooleanField(default=False)
    
    venta = models.ForeignKey(Venta,on_delete=models.CASCADE)

def get_default_profile_image():
    return '/fotoperfil.webp'

class PerfilUsuario(models.Model):
    foto = models.ImageField(upload_to='profile_images/', null=True, default=get_default_profile_image)
    rut = models.CharField(null=True, max_length=100)
    nombre = models.CharField(null=True, max_length=100)
    apellidop = models.CharField(null=True, max_length=100)
    apellidom = models.CharField(null=True, max_length=100)
    direccion = models.CharField(null=True, max_length=100)
    comuna = models.CharField(null=True, max_length=100)
    correo = models.EmailField(null=True, max_length=100)
    telefono = models.IntegerField(null=True)
    profesion = models.CharField(null=True, max_length=100)
    descripcion = models.CharField(null=True, max_length=100)
    fecha_nacimiento = models.DateField(null=True)
    #Contacto emergencia
    contacto_emergencia = models.IntegerField(null=True)
    nombre_emergencia = models.CharField(null=True, max_length=100)
    parentesco_emergencia = models.CharField(null=True, max_length=100)

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

class DatosTransferencia(models.Model):
    d_nombre = models.CharField(null=True, max_length=100)
    d_rut = models.CharField(null=True, max_length=100)
    d_correo = models.EmailField(null=True, max_length=100)
    d_banco = models.CharField(null=True, max_length=100)
    d_tipo_cuenta = models.CharField(null=True, max_length=100)
    d_numero_cuenta = models.CharField(null=True, max_length=100)

    d_usuario = models.OneToOneField(User, on_delete=models.CASCADE)

class Documento(models.Model):
    nombre = models.CharField(max_length=100)
    archivo = models.FileField()
    descripcion = models.CharField(max_length=100)

    perfil = models.ForeignKey(PerfilUsuario,on_delete=models.CASCADE)

class Boleta_Honorario(models.Model):
    numero = models.IntegerField(null=True)
    archivo = models.FileField(null=True)
    total = models.IntegerField()
    cantidad_evaluaciones = models.IntegerField(null=True)
    retencion = models.IntegerField(null=True)
    fecha = models.DateField()

    colaborador = models.ForeignKey(PerfilUsuario,on_delete=models.CASCADE)

class Costos_fijos(models.Model):
    numero = models.IntegerField(null=True)
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(null=True)
    fecha = models.DateField()
    impuesto = models.IntegerField(null=True)
    total = models.IntegerField()

class Costos_variables(models.Model):
    numero = models.IntegerField(null=True)
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(null=True)
    fecha = models.DateField()
    impuesto = models.IntegerField(null=True)
    total = models.IntegerField()