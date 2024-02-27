from django.urls import path
from django.contrib import admin


from .views import iniciar_sesion, logout_view, verificar_credenciales, panel_posgrados, actualizar_checkbox, recibir_archivo
app_name = 'cordins'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', iniciar_sesion, name='iniciar_sesion'),
    path('logout/', logout_view, name='logout_view'),
    path('verificar_credenciales/', verificar_credenciales, name='verificar_credenciales'),
    path('panel_posgrados/', panel_posgrados, name='panel_posgrados'),
    path('actualizar_checkbox/', actualizar_checkbox, name='actualizar_checkbox'),
    path('recibir_archivo/', recibir_archivo, name='recibir_archivo'),
]