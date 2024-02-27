from django.urls import path, include
from django.contrib import admin
from capcursapp.views import verificar_credenciales, mostrar_cursos, crear_capcurs, actualizar_curso, eliminar_curso,\
    agregar_curso, editar_curso, agregar_colab_edit, buscar_elemento, guardar_colaboradores, agregar_colab,\
    vista_previa, hay_colabs, verificar_curso_existente, guardar_enviar, elimina_colaborador, generarPDF, iniciar_sesion, cursos_guardados, logout_view

app_name = 'capcursapp'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', iniciar_sesion, name='iniciar_sesion'),
    path('verificar_credenciales/', verificar_credenciales, name='verificar_credenciales'),
    path('mostrar_cursos/', mostrar_cursos, name='mostrar_cursos'),
    path('agregar_curso/', agregar_curso, name='agregar_curso'),
    path('buscar_elemento/', buscar_elemento, name='buscar_elemento'),
    path('crear_capcurs/', crear_capcurs, name='crear_capcurs'),
    path('editar_curso/<int:id_curso>/', editar_curso, name='editar_curso'),
    path('actualizar_curso/<int:id_curso>/', actualizar_curso, name='actualizar_curso'),
    path('eliminar_curso/<int:id_curso>/', eliminar_curso, name='eliminar_curso'),
    path('agregar_colab/<str:cve_curso>/', agregar_colab, name='agregar_colab'),
    path('agregar_colab_edit/<str:cve_curso>/', agregar_colab_edit, name='agregar_colab_edit'),
    path('guardar_colaboradores/', guardar_colaboradores, name='guardar_colaboradores'),
    path('vista_previa/<str:nom_program>/', vista_previa, name='vista_previa'),
    path('hay_colabs/<str:cve_curso>/', hay_colabs, name='hay_colabs'),
    path('verificar_curso_existente/', verificar_curso_existente, name='verificar_curso_existente'),
    path('guardar_enviar/<str:nom_program>/', guardar_enviar, name='guardar_enviar'),
    path('elimina_colaborador/', elimina_colaborador, name='elimina_colaborador'),
    path('generarPDF/', generarPDF, name='generarPDF'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('cursos_guardados/', cursos_guardados, name='cursos_guardados'),
    path('logout/', logout_view, name='logout'),
]
