
from django.urls import path
from home import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('perfil/', views.ver_perfil_usuario, name='perfilusuario'),
    path('editarperfil/', views.editar_perfil_usuario, name='editarperfilusuario'),
    path('eliminar_documento/', views.eliminar_documento, name='eliminar_documento'),
    path('descargar_documento/<int:documento_id>/', views.descargar_documento, name='descargar_documento'),



]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)