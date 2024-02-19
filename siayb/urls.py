from django.urls import path, include
from django.contrib import admin
from siayb.views import (inicio_siayb, logout_view, verificar_credenciale_siayb, mis_cursos_siayb, selecciona_cursoAyB,
                         buscar_curso_ayb, hay_colaboradores, crea_asistiraAyB, crea_asistira690, elimina_uncurso,
                         elimina_inv_690, guardar_boletayb, recibir_archivo, generarPDF, altas_bajas)


app_name = 'siayb'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio_siayb, name='inicio_siayb'),
    path('logout/', logout_view, name='logout_view'),
    path('verificar_credenciale_siayb/', verificar_credenciale_siayb, name='verificar_credenciale_siayb'),
    path('mis_cursos_siayb/', mis_cursos_siayb, name='mis_cursos_siayb'),
    path('selecciona_cursoAyB/', selecciona_cursoAyB, name='selecciona_cursoAyB'),
    path('buscar_curso_ayb/', buscar_curso_ayb, name='buscar_curso_ayb'),
    path('hay_colaboradores/<cve_curso>/', hay_colaboradores, name='hay_colaboradores'),
    path('crea_asistiraAyB/', crea_asistiraAyB, name='crea_asistiraAyB'),
    path('crea_asistira690/', crea_asistira690, name='crea_asistira690'),
    path('elimina_uncurso/<int:id_sinsevi>/', elimina_uncurso, name='elimina_uncurso'),
    path('elimina_inv_690/<int:id_curso>/', elimina_inv_690, name='elimina_inv_690'),
    path('guardar_boletayb/', guardar_boletayb, name='guardar_boletayb'),
    path('recibir_archivo/', recibir_archivo, name='recibir_archivo'),
    path('generarPDF/', generarPDF, name='generarPDF'),
    path('altas_bajas/', altas_bajas, name='altas_bajas'),
    ]

