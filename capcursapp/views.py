from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponseBadRequest
from .forms import CapcursForm, ImpareguForm
from .models import Academic, Coordinaciones, Capcurs, Catacurs, Imparegu
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
COMMASPACE = ', '
import smtplib
from django.forms.models import model_to_dict
from django.contrib.auth import logout
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
import json


def iniciar_sesion(request):
    # Cerrar sesión (antes de redireccionar)
    return render(request, 'iniciosesion.html')


def logout_view(request):
    logout(request)
    return redirect('capcursapp:iniciar_sesion')


def verificar_credenciales2(request):
    messages.error(request, 'El sistema aún no está disponible.')
    return render(request, 'fuera_de_linea.html')


def verificar_credenciales(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['usuario_id'] = user.id
            return redirect('capcursapp:mostrar_cursos')
        else:
            # Las credenciales son inválidas
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'iniciosesion.html')
    else:
        return render(request, 'iniciosesion.html')


def cursos_guardados(request):
    periodo = settings.PERIODO
    anio = settings.ANIO
    usuario = request.user
    coordinacion = Coordinaciones.objects.filter(username=usuario.username).first()

    cursos_posgra = Capcurs.objects.filter(cve_program=coordinacion.cve_program)

    print('Se enviaron los datos de:', usuario )
    return render(request, 'cursos_guardados.html', {'coordinacion': coordinacion,
                                                     'cursos_posgra': cursos_posgra, 'periodo':periodo, 'anio': anio})


def eliminar_colab_sin_titular():
    # Obtener la lista de cursos
    cursos = Imparegu.objects.filter()

    for curso in cursos:
        # Verificar si hay titulares y colaboradores para el curso actual en Imparegu
        tiene_titulares = Imparegu.objects.filter(cve_curso=curso.cve_curso, participa='TITULAR').exists()
        tiene_colaboradores = Imparegu.objects.filter(cve_curso=curso.cve_curso, participa='COLABORADOR').exists()

        # Si hay colaboradores pero no titulares, eliminar todos los registros relacionados con el curso en Imparegu
        if tiene_colaboradores and not tiene_titulares:
            Imparegu.objects.filter(cve_curso=curso.cve_curso).delete()


def mostrar_cursos(request):
    usuario_id = request.session.get('usuario_id')
    periodo = settings.PERIODO
    anio = settings.ANIO

    if not usuario_id:
        return redirect('capcursapp:iniciar_sesion')

    try:
        coordinacion = Coordinaciones.objects.get(id=usuario_id)
        coordinacion.incrementar_cont_veces()  # Incrementa el valor de cont_veces en 1

        if coordinacion.cont_final >= 1:
            # El usuario ya ha generado el PDF, redirige a otra página o muestra un mensaje
            return redirect('capcursapp:cursos_guardados')


        miscursospersonal = Capcurs.objects.filter(cve_program=coordinacion.cve_program)
        #eliminar_colab_sin_titular() # revisar que no haya colaboradores sin titulares

    except Coordinaciones.DoesNotExist:
        messages.error(request, 'Usuario o contraseña incorrectos.')
        return redirect('capcursapp:iniciar_sesion')

    return render(request, 'mostrarcursos.html', {'miscursospersonal': miscursospersonal, 'usuario': coordinacion, 'periodo': periodo, 'anio': anio})


def generar_capcurs(request, cve_curso, periodo, tiene_colab, tiene_practicas, cve_academic, lunes_ini, lunes_fin,
                    martes_ini, martes_fin, miercoles_ini, miercoles_fin, jueves_ini, jueves_fin, viernes_ini, viernes_fin, aula):
    # Acceder al objeto "loscursos" de la variable "cursos_unicos"
    cursos_unicos = agregar_curso(request)
    cursos = cursos_unicos.get(cve_curso, [])

    if not cursos:
        return JsonResponse({'status': 'error', 'message': 'No se encontró un curso con el cve_curso especificado.'})

    # Obtener las propiedades del curso
    curso = cursos[0]
    cve_program = curso.cve_program
    nom_curso = curso.nom_curso
    creditos = curso.credima
    agno = curso.agno

    try:
        academic = Academic.objects.get(id=cve_academic)
    except Academic.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No se encontró un Academic con el ID especificado.'})
    nom_academic = academic.nombres
    apellidos = academic.apellidos
    capcurs = Capcurs(cve_curso=cve_curso, periodo=periodo, agno=agno, tiene_colab=tiene_colab,
                      tiene_practicas=tiene_practicas, cve_program=cve_program, nom_curso=nom_curso,
                      cve_academic=academic, nom_academic=nom_academic, apellidos=apellidos, creditos=creditos,
                      lunes_ini=lunes_ini, lunes_fin=lunes_fin, martes_ini=martes_ini, martes_fin=martes_fin,
                      miercoles_ini=miercoles_ini, miercoles_fin=miercoles_fin, jueves_ini=jueves_ini,
                      jueves_fin=jueves_fin, viernes_ini=viernes_ini, viernes_fin=viernes_fin, aula=aula)
    capcurs.save()
    # Devolver una respuesta de éxito
    return JsonResponse({'status': 'success'})


def crear_capcurs(request):
    if request.method == 'POST':
        print('Si es post')
        form_capcurs = CapcursForm(request.POST)
        form_imparegu = ImpareguForm(request.POST)

        if form_capcurs.is_valid() and form_imparegu.is_valid():
            print('Si es valido')
            # Obtener datos del formulario Capcurs
            cve_curso = request.POST.get('cve_curso', None)
            cve_academic = request.POST.get('cve_academic', None)

            catacurs = Catacurs.objects.filter(cve_curso=cve_curso, vigente="S").first()
            academic = Academic.objects.filter(cve_academic=cve_academic).first()

            if not catacurs:
                return JsonResponse(
                    {'status': 'error', 'message': 'No se encontró un curso con el cve_curso especificado.'})
            if not academic:
                return JsonResponse({'status': 'error', 'message': 'No se encontró un Academic con el ID especificado.'})

            # Crear registro Capcurs curso nuevo
            capcurs = form_capcurs.save(commit=False)
            capcurs.nombre = catacurs.nombre
            capcurs.cve_program = catacurs.cve_program
            capcurs.creditos = catacurs.credima
            capcurs.periodo = settings.PERIODO  # por defecto
            capcurs.agno = settings.ANIO
            capcurs.nom_academic = academic.nombres
            capcurs.apellidos = academic.apellidos
            capcurs.participacion = 'TITULAR'
            capcurs.save()
            print('Se guardo segun')

            # Crear registros Imparegu de Tilular
            imparegu = Imparegu()
            imparegu.cve_curso = cve_curso
            imparegu.cve_academic = cve_academic
            imparegu.agno = settings.ANIO  # por defecto
            #El resto de información se obtien de imparegubda existente

            imparegu.num_emplea = academic.num_emplea
            imparegu.periodo = settings.PERIODO  # por defecto
            imparegu.registro = '1753-01-01'
            imparegu.per_vi_cur = catacurs.periodo
            imparegu.ano_vi_cur = catacurs.agno
            imparegu.participa = 'TITULAR'
            imparegu.dis_cre = 0
            imparegu.save()
            return JsonResponse({'success': True})
        else:
            print('NO ES VALIDO')
            print(form_capcurs.errors)
            print(form_imparegu.errors)
            return JsonResponse({'success': False})
    else:
        form_capcurs = CapcursForm()
        form_imparegu = ImpareguForm()
    return JsonResponse({'success': True})


def academic_to_dict(academic):
    return {
        'id': academic.id,
        'cve_academic': academic.cve_academic,
        'nombres': academic.nombres,
        'apellidos': academic.apellidos,
        'cve_sexo': academic.cve_sexo,
        'cve_campus': academic.cve_campus,
        'cve_institu': academic.cve_institu,
        'cve_program': academic.cve_program,
        'email': academic.email
    }


#envia informacion del objeto usuario, loscursos y academicos
def agregar_curso(request):
    global loscursos, academicos
    usuario_id = request.session.get('usuario_id')
    usuario = Coordinaciones.objects.get(id=usuario_id)

    try:
        # Obtener todos los registros de la tabla Catacurs que tienen la misma cve_program que el usuario

        todos_los_cursos = Catacurs.objects.filter(cve_program=usuario.cve_program, vigente="S")
        # los cursos a excluir
        esp = usuario.cve_program + str(670)
        inv = usuario.cve_program + str(690)
        exg = usuario.cve_program + str(691)
        epd = usuario.cve_program + str(692)
        est = 'EST' + str(690)

        # Crear lista de claves a excluir
        excluir = [esp, inv, exg, epd, est]

        # Excluir los cursos con claves contenidas en la lista "excluir"
        loscursos = todos_los_cursos.exclude(cve_curso__in=excluir).order_by('cve_curso')

        # Academicos activos
        academicos_activos = Academic.objects.filter(activo='S')
        academicos = academicos_activos.order_by('cve_academic')
    except Academic.Catacurs:
        messages.error(request, 'Lo siento, elemento no encntrado en la base de datos')

    clave = ['AEC', 'BOT', 'COA', 'DES', 'ECO', 'EDA', 'ENT', 'ECD', 'FIV', 'FIT', 'FOR', 'FRU', 'GAN', 'GEN', 'HID', 'IDI', 'SEM']
    valor = ['AGROECOLOGÍA Y SUSTENTABILIDAD', 'BOTANICA', 'CÓMPUTO APLICADO', 'DESARROLLO RURAL', 'ECONOMÍA',
             'EDAFOLOGÍA', 'ENTOMOLOGÍA Y ACAROLOGIA','ESTADISTICA Y CIENCIA DE DATOS', 'FISIOLOGIA VEGETAL', 'FITOPATOLOGIA',
             'CIENCIAS FORESTALES', 'FRUTICULTURA', 'GANADERIA', 'GENETICA', 'HIDROCIENCIAS', 'IDIOMAS', 'PRODUCCIÓN DE SEMILLAS']

    programas = dict(zip(clave, valor))

    academicos_por_programa = {}

    for programa in clave:
        # Obtener los profesores que pertenecen al programa actual
        # idiomas se quita el doctorado porque son licenciaturas
        #academicos = Academic.objects.filter(cve_program=programa, activo='S', grado='DOCTORADO').order_by('cve_academic')
        academicos = Academic.objects.filter(cve_program=programa, activo='S').order_by('cve_academic')
        academicos_por_programa[programa] = [academic_to_dict(academico) for academico in academicos]

    academicos_por_programa_json = json.dumps(academicos_por_programa)

    return render(request, 'agrega_curso.html', {'loscursos': loscursos,
                                                 'usuario': usuario,
                                                 'programas': programas,
                                                 'academicos_por_programa_json': academicos_por_programa_json})


# vista que busca al curso seleccionado y devuelve el objeto
def buscar_elemento(request):
    elemento_seleccionado = request.GET.get('elemento')
    tipo_elemento = request.GET.get('tipo_elemento')
    cve_program = request.GET.get('cve_program')  # Obtener la clave del programa seleccionada

    try:
        if tipo_elemento == 'curso':
            elcurso = Catacurs.objects.filter(cve_curso=elemento_seleccionado).first()
            if elcurso is not None:
                data = {
                    'id_catacurs': elcurso.id,
                    'cve_curso': elcurso.cve_curso,
                    'creditos': elcurso.credima
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'error': 'No se encontró el curso seleccionado'})

        elif tipo_elemento == 'programa':
            elprofesor = Academic.objects.all(cve_program=cve_program)
            if elprofesor is not None:
                data = {
                    'nombres': elprofesor.nombres,
                    'apellidos': elprofesor.apellidos,
                    'correo': elprofesor.email,
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'error': 'No se encontró el profesor seleccionado'})

        elif tipo_elemento == 'profesor':
            elprofesor = Academic.objects.filter(cve_academic=elemento_seleccionado, cve_program=cve_program).first()
            if elprofesor is not None:
                data = {
                    'nombres': elprofesor.nombres,
                    'apellidos': elprofesor.apellidos,
                    'correo': elprofesor.email,
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'error': 'No se encontró el profesor seleccionado'})
        else:
            return JsonResponse({'error': 'Tipo de elemento no válido'})
    except Exception as e:
        #print(str(e))
        return JsonResponse({'error': str(e)})

def editar_curso(request, id_curso):
    usuario_id = request.session.get('usuario_id')
    usuario = Coordinaciones.objects.get(id=usuario_id)
    curso = Capcurs.objects.get(id=id_curso)
    form = CapcursForm(instance=curso)
    datos_curso = model_to_dict(curso)
    academicos1 = Academic.objects.all()
    academicos = academicos1.order_by('cve_academic')
    return render(request, 'editarcurso.html', {'form': form,
                                                'curso': curso,
                                                'datos_curso': datos_curso,
                                                'academicos': academicos,
                                                'usuario':usuario})


def actualizar_curso(request, id_curso):
    curso = get_object_or_404(Capcurs, pk=id_curso)

    # Crear una instancia de CapcursForm relacionada con el curso
    form = CapcursForm(request.POST, instance=curso)

    # Obtener la instancia de Imparegu usando el ID
    id_imparegu = Imparegu.objects.get(cve_curso=curso.cve_curso, cve_academic=curso.cve_academic_id)
    imparegu_instance = get_object_or_404(Imparegu, pk=id_imparegu.id_auto)

    print(id_imparegu.cve_curso, id_imparegu.cve_academic)

    # Crear una instancia de ImpareguForm relacionada con la instancia de Imparegu
    formIMpa = ImpareguForm(request.POST, instance=imparegu_instance)

    # Obtener el valor de id_catacurs y agregarlo a ambos formularios
    id_catacurs = request.POST.get('id_catacurs')

    # Crear una copia mutable del QueryDict
    mutable_request_post = request.POST.copy()

    mutable_request_post['id_catacurs'] = id_catacurs
    form.data = mutable_request_post
    formIMpa.data = mutable_request_post

    if request.method == 'POST' and form.is_valid() and formIMpa.is_valid():
        form.save()
        formIMpa.save()
        messages.success(request, 'El curso se ha actualizado correctamente.')
        return redirect('capcursapp:mostrar_cursos')
    else:
        errors = form.errors.as_json()
        return JsonResponse({'success': False, 'error': errors})


@ensure_csrf_cookie
def elimina_colaborador(request):
    #print('Se esta ejecutando')
    if request.method == 'POST':
        #print('Si es post')
        #print(request.POST)
        cve_academic = request.POST.get('cve_academic')
        cve_curso = request.POST.get('cve_curso')
        #print('profe y curso ', cve_academic, cve_curso )
        colabo = Imparegu.objects.filter(cve_curso=cve_curso, cve_academic=cve_academic, participa='Colaborador').first()
        #print('Se va este man: ', colabo)
        colabo.delete()
        messages.success(request, 'El colaborador ha sido eliminado correctamente.')
        #print(' Ya fue')
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})


def eliminar_curso(request, id_curso):
    print('entro a la funcion')
    if request.method == 'GET':
        try:
            curso = Capcurs.objects.get(pk=id_curso)
        except Capcurs.DoesNotExist:
            return JsonResponse({'error': 'El curso no existe'}, status=404)

        impare_list = Imparegu.objects.filter(cve_curso=str(curso.cve_curso))

        impare_list.delete()
        curso.delete()
        messages.success(request, 'El curso se ha eliminado correctamente.')
        return redirect('capcursapp:mostrar_cursos')
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def eliminar_curso_1(request, id_curso):
    curso = Capcurs.objects.get(pk=id_curso)
    clave = curso.cve_curso_id
    impare_list = Imparegu.objects.filter(cve_curso=str(clave)) #clave que viene de url debo tratarlo como str
    if request.method == 'POST':
        # Si se confirma la eliminación del curso mediante un formulario POST
        curso.delete()  # Elimina el registro de la tabla Capcurs
        impare_list.delete()  # Elimina todos los registros de la tabla Imparegu
        response_data = {'message': 'Curso eliminado satisfactoriamente'}
        return HttpResponseBadRequest(json.dumps(response_data))
    else:
        # Si se accede a la función mediante un método HTTP distinto de POST
        return render(request, 'eliminarcurso.html', {'curso': curso})


def agregar_colab(request, cve_curso):
    curso = Catacurs.objects.filter(cve_curso=cve_curso).first()

    # Obtener la lista de programas disponibles
    clave = ['AEC', 'BOT', 'COA', 'DES', 'ECO', 'EDA', 'ENT', 'ECD', 'FIV', 'FIT', 'FOR', 'FRU', 'GAN', 'GEN', 'HID',
             'SEM']
    valor = ['AGROECOLOGÍA Y SUSTENTABILIDAD', 'BOTANICA', 'CÓMPUTO APLICADO', 'DESARROLLO RURAL', 'ECONOMÍA',
             'EDAFOLOGÍA', 'ENTOMOLOGÍA Y ACAROLOGIA', 'ESTADISTICA Y CIENCIA DE DATOS', 'FISIOLOGIA VEGETAL', 'FITOPATOLOGIA',
             'CIENCIAS FORESTALES', 'FRUTICULTURA', 'GANADERIA', 'GENETICA', 'HIDROCIENCIAS', 'PRODUCCIÓN DE SEMILLAS'
             ]

    programas = dict(zip(clave, valor))

    academicos_por_programa = {}
    for programa in clave:
        # Obtener los profesores que pertenecen al programa actual
        academicos = Academic.objects.filter(cve_program=programa, grado='DOCTORADO', activo='S').order_by('cve_academic')
        academicos_por_programa[programa] = [academic_to_dict(academico) for academico in academicos]

    academicos_por_programa_json = json.dumps(academicos_por_programa)

    return render(request, 'agrega_colab.html', {'curso': curso, 'programas': programas,
                                                 'academicos_por_programa_json': academicos_por_programa_json})


def agregar_colab_edit(request, cve_curso):
    curso = Capcurs.objects.filter(cve_curso=cve_curso).first()

    # Obtener la lista de programas disponibles
    clave = ['AEC', 'BOT', 'COA', 'DES', 'ECO', 'EDA', 'ENT', 'ECD', 'FIV', 'FIT', 'FOR', 'FRU', 'GAN', 'GEN', 'HID',
             'SEM']
    valor = ['AGROECOLOGÍA Y SUSTENTABILIDAD', 'BOTANICA', 'CÓMPUTO APLICADO', 'DESARROLLO RURAL', 'ECONOMÍA',
             'EDAFOLOGÍA', 'ENTOMOLOGÍA Y ACAROLOGIA', 'ESTADISTICA Y CIENCIA DE DATOS', 'FISIOLOGIA VEGETAL', 'FITOPATOLOGIA',
             'CIENCIAS FORESTALES', 'FRUTICULTURA', 'GANADERIA', 'GENETICA', 'HIDROCIENCIAS', 'PRODUCCIÓN DE SEMILLAS']

    programas = dict(zip(clave, valor))

    academicos_por_programa = {}
    for programa in clave:
        # Obtener los profesores que pertenecen al programa actual
        academicos = Academic.objects.filter(cve_program=programa, activo='S').order_by('cve_academic')
        academicos_por_programa[programa] = [academic_to_dict(academico) for academico in academicos]

    academicos_por_programa_json = json.dumps(academicos_por_programa)

    return render(request, 'agrega_colab_edit.html',
                  {'curso': curso, 'programas': programas, 'academicos_por_programa_json': academicos_por_programa_json})


def guardar_colaboradores(request):
    if request.method == 'POST':
        cve_curso = request.POST.get('cve_curso')
        form = ImpareguForm(request.POST)

        if form.is_valid():
            profesores_seleccionados = request.POST.get('profesores_seleccionados')

            if not profesores_seleccionados:
                return HttpResponseBadRequest('El campo "profesores_seleccionados" no puede estar vacío.')

            profesores_seleccionados = json.loads(profesores_seleccionados)

            for cve_academic_sel in profesores_seleccionados:
                if cve_academic_sel == 'A00000':
                    return JsonResponse({'status': 'success'})
                else:
                    academic_imp = Academic.objects.filter(cve_academic=cve_academic_sel).first()
                    datos_catacurs = Catacurs.objects.filter(cve_curso=cve_curso).first()
                    imparegu = Imparegu.objects.create(
                        cve_curso=cve_curso,
                        cve_academic=cve_academic_sel,
                        agno=settings.ANIO,
                        num_emplea=academic_imp.num_emplea,
                        periodo=settings.PERIODO,
                        registro='1753-01-01',
                        per_vi_cur=datos_catacurs.periodo,
                        ano_vi_cur=datos_catacurs.agno,
                        participa='COLABORADOR',
                        dis_cre=0
                    )
                    imparegu.save()
                    messages.success(request, '¡Colaboradores agregados exitosamente!')

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'errors'})
    else:
        form = ImpareguForm()
    return render(request, 'agrega_colab.html', {'form': form})

def vista_previa(request, nom_program):
    usuario = Coordinaciones.objects.get(nom_program=nom_program)
    cve_program = usuario.cve_program
    cursos_posgra = Capcurs.objects.filter(cve_program=cve_program)

    colaboradores = Imparegu.objects.filter(participa='Colaborador')
    periodo = settings.PERIODO
    anio = settings.ANIO

    cve_academic_list = [colaborador.cve_academic for colaborador in colaboradores]
    datos_academicos = Academic.objects.filter(cve_academic__in=cve_academic_list)

    return render(request, 'vista_previa.html', {'usuario': usuario, 'cursos_posgra': cursos_posgra,
                                                 'colaboradores': colaboradores, 'datos_academicos': datos_academicos,
                                                 'periodo': periodo, 'anio': anio})



def hay_colabs(request, cve_curso):
    colaboradores = Imparegu.objects.filter(cve_curso=cve_curso, participa='Colaborador')
    data = []
    for colab in colaboradores:
        profesor = Academic.objects.filter(cve_academic=colab.cve_academic).first()
        data.append({
            'clave': profesor.cve_academic,
            'nombre': profesor.nombres,
            'apellido': profesor.apellidos,
        })
    return JsonResponse({'data': data}) # Devolver un objeto JSON con el campo 'data'

#verificar si un curso ya existe
def verificar_curso_existente(request):
    cve_curso = request.GET.get('cve_curso')
    cve_academic = request.GET.get('cve_academic')

    cursos = Capcurs.objects.filter(cve_curso=cve_curso, cve_academic=cve_academic)
    if cursos.exists():
        return JsonResponse({'existe': True})
    else:
        return JsonResponse({'existe': False})


def guardar_enviar(request, nom_program):
    usuario = Coordinaciones.objects.get(nom_program=nom_program)
    cve_program = usuario.cve_program
    cursos_posgra = Capcurs.objects.filter(cve_program=cve_program)

    colaboradores = Imparegu.objects.filter(participa='Colaborador')
    cve_academic_list = [colaborador.cve_academic for colaborador in colaboradores]
    datos_academicos = Academic.objects.filter(cve_academic__in=cve_academic_list)

    periodo = settings.PERIODO
    anio = settings.ANIO

    return render(request, 'guardar_enviar.html', {'usuario': usuario, 'cursos_posgra': cursos_posgra,
                                                   'colaboradores': colaboradores, 'datos_academicos': datos_academicos,
                                                   'periodo': periodo, 'anio': anio})


# IMplementacion de envio de pdf
def generarPDF(request):
    if request.method == 'POST':
        elusuario = request.user
        usuario = Coordinaciones.objects.filter(username=elusuario.username).first()
        archivo_adjunto = request.FILES.get('pdf')
        # Envía el correo electrónico
        #destinatario = ['rodriguez.rosales@colpos.mx']
        destinatario = ['servacadmontecillo@colpos.mx', 'sistema.inscripcioncm@colpos.mx', 'sinscripcolpos@gmail.com', usuario.username]

        asunto = 'Cursos Programados' + ' ' + usuario.cve_posgrad + '-' + usuario.nom_program
        periodo = settings.PERIODO
        anio = settings.ANIO
        mensaje = 'C O L E G I O   D E   P O S T G R A D U A D O S\n'
        mensaje += 'C A M P U S   M O N T E C I L L O\n\n'
        mensaje += 'Se adjunta documento PDF de los cursos programados para el periodo de ' + periodo + '_' + str(anio) + '_' + usuario.cve_posgrad + '_' + usuario.nom_program
        mensaje += '\n\nATENTAMENTE\n\n'
        mensaje += 'SUBDIRECCION ACADEMICA'

        mensaje_plano = strip_tags(mensaje)

        # Crear el objeto EmailMultiAlternatives
        email = EmailMultiAlternatives(
            asunto,
            str(mensaje_plano),
            'SISTEMA DE CAPTURA DE CURSOS EN LINEA',
            destinatario
        )

        # crear nombre del archivo
        nombre_archivo = f'{usuario.nom_program}-{settings.PERIODO}_{settings.ANIO}.pdf'
        archivo_adjunto.name = nombre_archivo

        # Adjuntar el archivo PDF al correo electrónico
        email.attach(archivo_adjunto.name, archivo_adjunto.read(), 'application/pdf')

        # Envía el correo electrónico utilizando SMTP
        try:
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            smtp_usuario = 'sinscripcolpos@gmail.com'
            smtp_password = 'zapj lqre wdod tqwt'   # Asegúrate de utilizar las credenciales correctas
            smtp = smtplib.SMTP(smtp_server, smtp_port)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(smtp_usuario, smtp_password)
            smtp.sendmail(smtp_usuario, destinatario, email.message().as_bytes())

            smtp.quit()
            #print('La enviación')
            coordinacion = Coordinaciones.objects.get(id=usuario.id)
            coordinacion.incrementar_cont_final()
            #print('Ya es uno', coordinacion)
            messages.success(request, '¡Correo electrónico enviado correctamente!')
            # Redirige a la página 'cursos_guardados'
            print('La enviación')
            return redirect('capcursapp:cursos_guardados')
        except smtplib.SMTPException as e:
            messages.success(request, '¡Correo electrónico no enviado, intente de nuevo!')
            return HttpResponseBadRequest(f'Error al enviar el correo electrónico: {str(e)}')
    return HttpResponseBadRequest('Error al generar el PDF')
