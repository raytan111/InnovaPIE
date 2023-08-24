
from django.urls import path
from colaboradores import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

#Urls de Colaboradores
    path('', views.listar_usuarios, name='listar_usuarios'),
    path('registrar/', views.crear_usuario, name='registrar_usuario'),
    path('perfil/<id>/', views.ver_perfil_usuario, name='perfil_usuario'),
    path('editarperfil/<id>/', views.editar_perfil_usuario, name='editar_perfil_usuario'),

    path('editaruser/<int:user_id>/', views.editar_usuario, name='editar_usuario'),

    path('perfil/nuevo_documento/<int:id>/', views.nuevo_documento, name='nuevo_documento'),
    path('eliminar_usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('colaboradores/', views.listar_colaboradores, name='listar_colaboradores'),
    path('descargar_documento/<int:documento_id>/', views.descargar_documento, name='descargar_documento'),

    



]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)