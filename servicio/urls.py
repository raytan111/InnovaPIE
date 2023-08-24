from django.urls import path
from servicio import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.listaservicio, name="Lista Servicio"),
    path('registroservicio/', views.regservicio, name="Registro Servicio"),
    path('editarservicio/<id>/', views.editarservicio, name="Editar Servicio"),
    path('eliminar_servicio/<int:servicio_id>/', views.eliminar_servicio, name='eliminar_servicio'),

    

    

]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)