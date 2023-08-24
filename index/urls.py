from django.urls import path
from index import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views 


urlpatterns = [
    path('', views.vista_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('recuperar-contrasena/', views.recuperar_clave, name='recuperar_clave'),
    path('reset-password/<int:user_id>/<str:token>/', views.cambiar_clave, name='cambiar_clave'),



]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)