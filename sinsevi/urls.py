from django.urls import path, include
from django.contrib import admin
from sinsevi.views import inicio_sesionE

from .views import mis_cursos, verificar_credencialEst, selecciona_curso, buscar_curso, crea_asistira, crea_asistira690,\
    elimina_uncurso, logout_view, guardar_boleta, generarPDF, cursos_asistire, recibir_archivo, hay_colaboradores, elimina_inv_690,\
    est_sin_aeta, actualizar_cvu, fuera_de_linea

app_name = 'sinsevi'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio_sesionE, name='inicio_sesionE'),
    path('logout/', logout_view, name='logout_view'),
    path('verificar_credencialEst/', verificar_credencialEst, name='verificar_credencialEst'),
    path('mis_cursos/', mis_cursos, name='mis_cursos'),
    path('selecciona_curso/', selecciona_curso, name='selecciona_curso'),
    path('hay_colaboradores/<cve_curso>/', hay_colaboradores, name='hay_colaboradores'),
    path('buscar_curso/', buscar_curso, name='buscar_curso'),
    path('crea_asistira/', crea_asistira, name='crea_asistira'),
    path('crea_asistira690/', crea_asistira690, name='crea_asistira690'),
    path('elimina_uncurso/<int:id_sinsevi>/', elimina_uncurso, name='elimina_uncurso'),
    path('elimina_inv_690/<int:id_curso>/', elimina_inv_690, name='elimina_inv_690'),
    path('guardar_boleta/', guardar_boleta, name='guardar_boleta'),
    path('cursos_asistire/', cursos_asistire, name='cursos_asistire'),
    path('recibir_archivo/', recibir_archivo, name='recibir_archivo'),
    path('generarPDF/', generarPDF, name='generarPDF'),
    path('est_sin_aeta/', est_sin_aeta, name='est_sin_aeta'),
    path('actualizar_cvu/', actualizar_cvu, name='actualizar_cvu'),
    path('fuera_de_linea/', fuera_de_linea, name='fuera_de_linea'),
]

