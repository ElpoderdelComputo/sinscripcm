import json
import smtplib
import os
from django.contrib.auth import logout, login
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from SINSCRIP import settings
from sinsevi.models import CapcursappCoordinaciones, estudiante_consejero, Capcurs, Catacurs, Becarios, Asistira, Catabeca, \
    Imparegu, Estudian, Sinsevi, Estud_nacion, Catanaci, Orientador
from sinsevi.models import Academic
from sinsevi.forms import AsistiraForm, SinseviForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from PyPDF2 import PdfWriter, PdfReader
from io import BytesIO
from reportlab.pdfgen import canvas
from PIL import Image
from django.urls import reverse


# Create your views here.
def inicio_sesionE(request):
    # Cerrar sesión (antes de redireccionar)
    return render(request, 'inicio_sesionEst.html')


def logout_view(request):
    logout(request)
    return redirect('sinsevi:inicio_sesionE')

def about(request):
    return render(request, 'acerca_de.html')

def verificar_credencialEst(request):
    # Verificar si el sistema esta en linea
    if settings.sinsevi_on == 0:
        messages.error(request, 'El sistema aún no está disponible.')
        return render(request, 'fuera_de_linea.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print('usuario y pass: ',username, password)
        try:
            print('NO paso el user')
            user = Estudian.objects.get(username=username)
            print('Inicio sesion: ', str(user))
            if user.check_password(password):
                # Las credenciales son válidas
                login(request, user, backend='sinsevi.backends.EstudianBackend')
                request.session['usuario_id'] = user.id
                print('El usuario es: ', user.id)
                return redirect('sinsevi:mis_cursos')
            else:
                # Las credenciales son inválidas
                print('Las credenciales son inválidas')
                messages.error(request, 'Usuario o contraseña incorrectos.')
                return render(request, 'inicio_sesionEst.html')
        except Estudian.DoesNotExist:
            print('EL usuario no existe bro')
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'inicio_sesionEst.html')
    else:
        #print('no es post')
        return render(request, 'inicio_sesionEst.html')


def fuera_de_linea(request):
    return render(request, 'fuera_de_linea.html')


def mis_cursos(request):
    usuario_id = request.session.get('usuario_id')

    estudiante = get_object_or_404(Estudian, id=usuario_id)
    #valor de aeta


    print('vamos a ver si tiene aeta')
    if estudiante.aeta is False:
        return redirect('sinsevi:est_sin_aeta')

    if estudiante.consejop is False:
        return redirect('sinsevi:est_sin_aeta')

    if not usuario_id:
        return redirect('sinsevi:inicio_sesionE')

    try:
        estudiante.incrementar_cont_veces()
        if estudiante.cont_final >= 1: # cambiar de 5 a1
            return redirect('sinsevi:cursos_asistire')
    except Estudian.DoesNotExist:
        messages.error(request, 'El usuario no existe.')
        return redirect('sinsevi:inicio_sesionE')

    #recuperar datos del estudiate
    cve_estud = estudiante.cve_estud

    cve_program = estudiante.cve_program
    print('cve_program: ', cve_program)

    if cve_program == 'ECD':
        programa = get_object_or_404(CapcursappCoordinaciones, cve_program=cve_program)
        print('Es E C D: ', cve_program)
    elif cve_program == 'EST':
        programa = 'ESTADISTICA'
        print('Es E S T: ', cve_program)
    else:
        programa = get_object_or_404(CapcursappCoordinaciones, cve_program=cve_program)
        print('Es normal ', cve_program)


    beca = Becarios.objects.filter(cve_estud=cve_estud).first()
    if beca is None:
        cvu = ''
        entidad_beca = ''
    else:
        cvu = beca.cvu
        entidad_beca = Catabeca.objects.filter(cve_becaria=beca.cve_becaria).first()



    # Filtra los registros de la tabla Estudiante_Consejero donde el campo cve_estud coincida con el valor de cve_estud.
    fecha_nuevo_ingr = settings.FN_INGRESO

    try:
        consejero_estudiante = estudiante_consejero.objects.get(cve_estud=cve_estud)
        consejero = Academic.objects.get(cve_academic=consejero_estudiante.cve_academic)
    except estudiante_consejero.DoesNotExist:
        if estudiante.fechingr == fecha_nuevo_ingr:
            consejero = 'Nuevo Ingreso'
            print('Es de nuevo ingreso, sin consejero')
        else:
            consejero = 'No Registrado'  # O cualquier otro valor predeterminado que desees asignar si no hay consejero.
            print('No ha registrado consejo Particular')
    except Academic.DoesNotExist:
        # Aquí manejas la excepción si no se encuentra el objeto Academic
        consejero = 'Profesor no Registrado en Academic'

    #nacionalidad
    # Acceder a la tabla 'Estud_nacion' y filtrar por 'cve_estud'
    try:
        nacion = Estud_nacion.objects.get(cve_estud=estudiante.cve_estud)
        # Luego, acceder a la tabla 'Catanaci' y filtrar por 'cve_nacion' (suponiendo que 'nacion' contiene el registro que necesitas)
        pais = Catanaci.objects.get(cve_nacion=nacion.cve_nacion)
    except Estud_nacion.DoesNotExist:
        print('Se envía pais por defecto')
        pais = 'MEXICANA'  # O cualquier otro valor predeterminado que desees asignar en caso de que no exista un registro.

    # recuperar los cursos del estudiante
    capcursos = Sinsevi.objects.filter(cve_estud=cve_estud)  # Filtrar objetos
    cred_regular = 0
    cred_seminarios = 0
    cred_inv = 0

    for curso in capcursos:
        if cve_program == 'ECD':
            cve_program = 'EST'
        if curso.cve_curso in [str(cve_program) + '680', str(cve_program) + '681', str(cve_program) + '682']:
            cred_seminarios += curso.credima
        elif curso.cve_curso == str(cve_program) + '690':
            cred_inv += curso.credima
        else:
            cred_regular += curso.credima

    cred_inv = cred_inv-cred_regular
    if cred_inv <= 0:
        cred_inv = 0
    total = cred_regular + cred_seminarios + cred_inv
    suma_creditos = {
        'cred_seminarios': cred_seminarios,
        'cred_inv': cred_inv,
        'cred_regular': cred_regular,
        'total': total,
    }

    config = {
        'periodo': settings.PERIODO,
        'anio': settings.ANIO,
        'flimite': settings.FECHA_LIMITE
    }


    render_data = {
        'estudiante': estudiante, 'programa': programa, 'capcursos': capcursos, 'config': config, 'consejero': consejero,
        'entidad_beca': entidad_beca, 'pais': pais , 'suma_creditos': suma_creditos, 'cvu': cvu}

    return render(request, 'mis_cursos.html', render_data)

def est_sin_aeta(request):
    usuario_id = request.session.get('usuario_id')
    estudiante = get_object_or_404(Estudian, id=usuario_id)
    cve_program = estudiante.cve_program

    if cve_program == 'ECD':
        programa = get_object_or_404(CapcursappCoordinaciones, cve_program=cve_program)
        print('Es E C D: ', cve_program)
    elif cve_program == 'EST':
        programa = get_object_or_404(CapcursappCoordinaciones, cve_program='ECD')
        print('Es E S T: ', cve_program)
    else:
        programa = get_object_or_404(CapcursappCoordinaciones, cve_program=cve_program)
        print('Es normal ', cve_program)

    if estudiante.consejop is False and estudiante.aeta is False:
        advertencia = ("No ha registrado su Consejo Particular ni su Acta de Evaluación de Trabajo Académico.")
    elif estudiante.consejop is False:
        advertencia = "No ha registrado su Consejo Particular. Asegúrate de completar este requisito."
    elif estudiante.aeta is False:
        advertencia = "No ha registrado su Acta de Evaluación de Trabajo Académico. Asegúrate de completar este requisito."
    else:
        # Si ambos consejop y aeta están registrados, no hay necesidad de redirigir, puedes realizar alguna otra acción aquí.
        advertencia = "Consejo Particular y Acta de Evaluación de Trabajo Académico registrados."  # O un mensaje en blanco si no hay advertencia.

    return render(request, 'est_sin_aeta.html', {'estudiante':estudiante, 'programa': programa, 'advertencia': advertencia})


def curso_to_dict(curso):
    return {
        'id': curso.id,
        'nombre': curso.nombre,
        'cve_curso': curso.cve_curso
    }

def selecciona_curso(request):
    # Obtener todos los registros de la tabla CAPCURS
    print('Se ha dado el click man')
    usuario_id = request.session.get('usuario_id')
    usuario = Estudian.objects.get(id=usuario_id)

    # Verifica si el correo ya ha sido enviado
    if usuario.cont_final > 0:
        messages.warning(request, 'El correo ya ha sido enviado anteriormente.')
        return redirect('sinsevi:cursos_asistire')

    capcursos = Sinsevi.objects.filter(cve_estud=usuario.cve_estud)  # Filtrar objetos
    capcursos_count = capcursos.count()
    if capcursos_count == 6:
        mensaje = f"Usted tiene {capcursos_count} cursos. Sólo puede agregar hasta 6 cursos en el sistema."
        url = reverse('sinsevi:mis_cursos')
        return redirect(f"{url}?mensaje={mensaje}")

    los_cursos = Capcurs.objects.all()
    loscursos = los_cursos.order_by('cve_curso')
    clave = ['AEC', 'BOT', 'COA', 'DES', 'ECO', 'EDA', 'ENT', 'ECD', 'FIV', 'FIT', 'FOR', 'FRU', 'GAN', 'GEN', 'HID', 'IDI',
             'SEM']
    valor = ['AGROECOLOGÍA Y SUSTENTABILIDAD', 'BOTANICA', 'CÓMPUTO APLICADO', 'DESARROLLO RURAL', 'ECONOMÍA',
             'EDAFOLOGÍA', 'ENTOMOLOGÍA Y ACAROLOGIA', 'ESTADISTICA Y CIENCIA DE DATOS', 'FISIOLOGIA VEGETAL', 'FITOPATOLOGIA',
             'CIENCIAS FORESTALES', 'FRUTICULTURA', 'GANADERIA', 'GENETICA', 'HIDROCIENCIAS', 'IDIOMAS', 'PRODUCCIÓN DE SEMILLAS']

    programas = dict(zip(clave, valor))

    cursos_por_programa = {}
    for programa in programas:
        # Obtener los cursos que pertenecen al programa actual
        cursos = Capcurs.objects.filter(cve_program=programa).order_by('cve_curso')
        cursos_por_programa[programa] = [curso_to_dict(curso) for curso in cursos]
    cursos_por_programa_json = json.dumps(cursos_por_programa)

    return render(request, 'selecciona_curso.html', {
        'usuario': usuario,
        'loscursos': loscursos,
        'programas': programas,
        'cursos_por_programa_json': cursos_por_programa_json
    })


def buscar_curso(request):
    print('Lo estamos haciendo')
    id_curso = request.GET.get('id_curso')
    try:
        elcurso = Capcurs.objects.filter(id=id_curso).first()

        # Ahora, elcurso contiene el objeto Capcurs correcto según la selección del usuario
        #################
        print('EL curso de la consulta es: ', elcurso.cve_curso, elcurso.cve_academic_id)
        if elcurso is not None:
            data = {
                'id_curso': elcurso.id,
                'cve_academic': elcurso.cve_academic_id,
                'nom_academic': elcurso.nom_academic,
                'apellidos': elcurso.apellidos,
                'participacion': elcurso.participacion,
                'creditos': elcurso.creditos,
                'aula': elcurso.aula,
                'observaciones': elcurso.observaciones,
                'lunes_ini': elcurso.lunes_ini,
                'lunes_fin': elcurso.lunes_fin,
                'martes_ini': elcurso.martes_ini,
                'martes_fin': elcurso.martes_fin,
                'miercoles_ini': elcurso.miercoles_ini,
                'miercoles_fin': elcurso.miercoles_fin,
                'jueves_ini': elcurso.jueves_ini,
                'jueves_fin': elcurso.jueves_fin,
                'viernes_ini': elcurso.viernes_ini,
                'viernes_fin': elcurso.viernes_fin,
                'periodo': elcurso.periodo,
                'agno': elcurso.agno,
                'lunes_inip': elcurso.lunes_inip,
                'lunes_finp': elcurso.lunes_finp,
                'martes_inip': elcurso.martes_inip,
                'martes_finp': elcurso.martes_finp,
                'miercoles_inip': elcurso.miercoles_inip,
                'miercoles_finp': elcurso.miercoles_finp,
                'jueves_inip': elcurso.jueves_inip,
                'jueves_finp': elcurso.jueves_finp,
                'viernes_inip': elcurso.viernes_inip,
                'viernes_finp': elcurso.viernes_finp,
                'aulap': elcurso.aulap,
                'observacionesp': elcurso.observacionesp
            }
            #print('la data es: ', data)
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'No se encontró el curso seleccionado'})
    except Exception as e:
        print(str(e))
        return JsonResponse({'error': str(e)})


def hay_colaboradores(request, cve_curso):
    #print('Ya fuimos a buscar colabs')
    colaboradores = Imparegu.objects.filter(cve_curso=cve_curso, participa='COLABORADOR')
    data = []
    for colab in colaboradores:
        profesor = Academic.objects.filter(cve_academic=colab.cve_academic).first()
        data.append({
            'clave': profesor.cve_academic,
            'nombre': profesor.nombres,
            'apellido': profesor.apellidos,
        })
    return JsonResponse({'data': data})  # Devolver un objeto JSON con el campo 'data'


#funcion que agrega curso regular a asistirá y sisevi
def crea_asistira(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Estudian.objects.get(id=usuario_id)

    if usuario.cont_final > 0:
        messages.warning(request, 'El correo ya ha sido enviado anteriormente.')
        return redirect('sinsevi:cursos_asistire')

    if request.method == 'POST':
        form_asistira = AsistiraForm(request.POST)
        form_sinsevi = SinseviForm(request.POST)

        if form_asistira.is_valid() and form_sinsevi.is_valid():

            cve_curso = request.POST.get('cve_curso', None)
            id_curso = request.POST.get('id_curso', None)

            # Verificar si ya existe un registro con el mismo cve_curso y cve_estud
            asistira_existente = Asistira.objects.filter(cve_curso=cve_curso, cve_estud=usuario.cve_estud).first()
            if asistira_existente:
                return JsonResponse({'success': False, 'error': 'Ya agregaste este curso'})
            else:
                try:
                    # Intentar obtener el curso seleccionado con la combinación de id_curso y cve_academic
                    micurso = Capcurs.objects.get(id=id_curso)
                    catacurs = Catacurs.objects.get(id=micurso.id_catacurs_id)
                    asistira = form_asistira.save(commit=False)
                    asistira.cve_estud = usuario.cve_estud
                    asistira.cve_curso = cve_curso
                    asistira.cve_academic = micurso.cve_academic_id
                    asistira.gpo_670 = catacurs.gpo_670
                    asistira.califica = 0
                    asistira.creditos = micurso.creditos
                    asistira.periodo = settings.PERIODO
                    asistira.agno = settings.ANIO
                    asistira.observa = 'PEND.'
                    asistira.registro = '1753-01-01'
                    asistira.per_vi_cur = catacurs.periodo
                    asistira.ano_vi_cur = catacurs.agno
                    asistira.no_periodo = settings.NO_PERIODO
                    asistira.isevaluated = 0
                    asistira.save()
                    # asistiré creado

                    # Crea una instancia de Sinsevi y asigna el Capcurs
                    sinsevi = Sinsevi()
                    sinsevi.cve_estud = usuario.cve_estud
                    sinsevi.id_capcurs = micurso
                    sinsevi.cve_curso = cve_curso
                    sinsevi.nombre = micurso.nombre
                    sinsevi.credimi = catacurs.credimi
                    sinsevi.credima = catacurs.credima
                    sinsevi.cve_academic = micurso.cve_academic_id
                    sinsevi.nom_academic = micurso.nom_academic
                    sinsevi.apellidos = micurso.apellidos
                    sinsevi.gpo_670 = catacurs.gpo_670
                    sinsevi.save()
                    # sinsevi creado
                    return JsonResponse({'success': True})

                except Capcurs.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'El curso seleccionado no existe'})
        else:
            print(form_asistira.errors)
            print(form_sinsevi.errors)
            return JsonResponse({'success': False, 'error': 'Error en el formulario'})

    else:
        form_asistira = AsistiraForm()
        form_sinsevi =SinseviForm()

    return JsonResponse({'success': True})

# rodriguez.rosales@colpos.mx

#funcion que agrega INVESTIGACION
def crea_asistira690(request):
    # Obtener el ID de usuario de la sesión

    usuario_id = request.session.get('usuario_id')
    usuario = Estudian.objects.get(id=usuario_id)
    # Verifica si el correo ya ha sido enviado
    if usuario.cont_final > 0:
        messages.warning(request, 'El correo ya ha sido enviado anteriormente.')
        return redirect('sinsevi:cursos_asistire')

    capcursos = Sinsevi.objects.filter(cve_estud=usuario.cve_estud)  # Filtrar objetos
    capcursos_count = capcursos.count()
    if capcursos_count == 6:
        response_data = {'success': True, 'message': 'Sólo puede agregar hasta 6 cursos en el sistema.'}
        return JsonResponse(response_data)

    try:
        # Obtener el usuario
        usuario = Estudian.objects.get(id=usuario_id)
        # Calcular el código del curso
        if usuario.cve_program== 'ECD':
            codigo_690 = 'EST690'
        else:
            codigo_690 = usuario.cve_program + '690'

        # Verificar si el curso ya existe en la tabla Asistira
        if Asistira.objects.filter(cve_estud=usuario.cve_estud, cve_curso=codigo_690).exists():
            # El curso ya existe, enviar un mensaje de error.
            print('Ya existe')
            response_data = {'success': False, 'message': 'INVESTIGACIÓN ya ha sido agregado.'}
        else:
            # Obtener datos del investigador
            consejero_estudiante = estudiante_consejero.objects.filter(cve_estud=usuario.cve_estud).first()
            investigador = Imparegu.objects.filter(cve_curso=codigo_690,
                                                   cve_academic=consejero_estudiante.cve_academic).first()
            print('el curso y gpo ',codigo_690, investigador.gpo_670)
            # Obtener datos del curso en Catacurs
            #catacurs = Catacurs.objects.filter(cve_curso=codigo_690, gpo_670=investigador.gpo_670).first()
            catacurs = Catacurs.objects.get(cve_curso=codigo_690, gpo_670=investigador.gpo_670)
            print (catacurs.nombre)

            if catacurs is None:
                # Manejar el caso en que no se encuentre el curso en Catacurs
                response_data = {'success': False, 'message': 'Curso no encontrado en Catacurs.'}
            else:

                if investigador is None:
                    # Manejar el caso en que no se encuentre el investigador
                    print('No esta en imparegu 690 de ', investigador.cve_academic)
                    response_data = {'success': True, 'message': 'Investigador no encontrado.'}
                    return JsonResponse(response_data)
                else:
                    print('La creacion de estos registros')
                    # Crear registro Asistira nuevo
                    asistira = Asistira.objects.create(
                        cve_estud=usuario.cve_estud,
                        cve_curso=codigo_690,
                        gpo_670=investigador.gpo_670,
                        califica=0,
                        creditos=9,
                        periodo=settings.PERIODO,
                        agno=settings.ANIO,
                        observa='PEND.',  # valor por defecto
                        registro='1753-01-01',
                        per_vi_cur=catacurs.periodo,
                        ano_vi_cur=catacurs.agno,
                        no_periodo=settings.NO_PERIODO,  # valor por defecto primavera = 1 verano y otoño: 2,3
                        isevaluated=0  # cambiara a 1 cuando se haya evaluado
                    )

                    # Obtener datos del profesor
                    profesor = Academic.objects.filter(cve_academic=investigador.cve_academic).first()

                    # Crear registro Sinsevi
                    sinsevi = Sinsevi.objects.create(
                        cve_estud=usuario.cve_estud,
                        cve_curso=codigo_690,
                        nombre=catacurs.nombre,
                        credimi = catacurs.credimi,
                        credima = catacurs.credima,
                        cve_academic=investigador.cve_academic,
                        nom_academic=profesor.nombres,
                        apellidos=profesor.apellidos,
                        gpo_670=investigador.gpo_670,
                    )
                    # Agregar mensaje de éxito
                    response_data = {'success': True, 'message': 'INVESTIGACIÓN se ha agregado exitosamente.'}
    except Estudian.DoesNotExist:
        # Manejar el caso en que el usuario no existe
        print('No iniciaste sesion man')
        response_data = {'success': False, 'message': 'Usuario no encontrado.'}
    return JsonResponse(response_data)


def elimina_uncurso(request, id_sinsevi):
    usuario_id = request.session.get('usuario_id')
    estudiante = Estudian.objects.get(id=usuario_id)
    print('se ha dado click a eliminar id: ', id_sinsevi)
    elcurso = Sinsevi.objects.filter(id_sinsevi=id_sinsevi).first()

    asistira = Asistira.objects.get(cve_estud=estudiante.cve_estud, cve_curso=elcurso.cve_curso)

    print('Tonces eliminar: ', asistira.cve_curso)
    # El curso no se encontró en capcursapp, enviar mensaje de error

    sinsevi_instance = Sinsevi.objects.get(id_sinsevi=id_sinsevi)
    sinsevi_instance.delete()
    asistira.delete()  # Elimina todos los registros de la tabla asistira
    messages.success(request, 'Curso eliminado satisfactoriamente')

    return redirect('sinsevi:mis_cursos')

def elimina_inv_690(request, id_curso):
    usuario_id = request.session.get('usuario_id')
    estudiante = Estudian.objects.get(id=usuario_id)
    cve_program = estudiante.cve_program
    cve_estud = estudiante.cve_estud
    programa = get_object_or_404(CapcursappCoordinaciones, cve_program=cve_program)

    consejero_estudiante = estudiante_consejero.objects.filter(cve_estud=cve_estud).first()

    asistira = Asistira.objects.get(id=id_curso)  # obtengo el curso en asistira
    print('Tonces eliminar: ', asistira.cve_curso)
    # El curso no se encontró en capcursapp, enviar mensaje de error
    asistira.delete()  # Elimina todos los registros de la tabla asistira
    messages.success(request, 'Curso eliminado satisfactoriamente')
    return redirect('sinsevi:mis_cursos')


def guardar_boleta(request):
    usuario_id = request.session.get('usuario_id')
    periodo = settings.PERIODO
    anio = settings.ANIO
    estudiante = get_object_or_404(Estudian, id=usuario_id)

    # Verifica si el correo ya ha sido enviado
    if estudiante.cont_final > 0:
        messages.warning(request, 'El correo ya ha sido enviado anteriormente.')
        return redirect('sinsevi:cursos_asistire')

    #valor de aeta

    try:
        estudiante.incrementar_cont_veces()
        if estudiante.cont_final >= 5:
            return redirect('sinsevi:inicio_sesionE')
    except Estudian.DoesNotExist:
        messages.error(request, 'El usuario no existe.')
        return redirect('sinsevi:inicio_sesionE')

    #recuperar datos del estudiate
    cve_estud = estudiante.cve_estud
    cve_program = estudiante.cve_program
    if cve_program == 'ECD':
        programa = get_object_or_404(CapcursappCoordinaciones, cve_program=cve_program)

    elif cve_program == 'EST':
        programa = get_object_or_404(CapcursappCoordinaciones, cve_program='ECD')

    else:
        programa = get_object_or_404(CapcursappCoordinaciones, cve_program=cve_program)


    beca = Becarios.objects.filter(cve_estud=cve_estud).first()
    if beca is None:
        entidad_beca = Catabeca.objects.filter(cve_becaria=33).first()
    else:
        entidad_beca = Catabeca.objects.filter(cve_becaria=beca.cve_becaria).first()

    try:
        cvu = beca.cvu
    except:
        cvu = 0000

    # Filtra los registros de la tabla Estudiante_Consejero donde el campo cve_estud coincida con el valor de cve_estud.
    fecha_nuevo_ingr = settings.FN_INGRESO
    try:
        consejero_estudiante = estudiante_consejero.objects.get(cve_estud=cve_estud)
        consejero = Academic.objects.get(cve_academic=consejero_estudiante.cve_academic)
        consejero_orientador = 'PROFESOR(A) CONSEJERO'
    except estudiante_consejero.DoesNotExist:
        #buscamos en la tabla orientador
        consejero_estudiante = Orientador.objects.get(cve_estud=cve_estud)
        consejero = Academic.objects.get(cve_academic=consejero_estudiante.cve_academic)
        consejero_orientador = 'PROFESOR(A) ORIENTADOR(A)'
    except Orientador.DoesNotExist:
        # buscamos en la tabla orientador
        consejero_estudiante = 'SIN DATOS'
        consejero = 'SIN DATOS'
        consejero_orientador = 'PROFESOR(A) ORIENTADOR(A)'


    #nacionalidad
    # Acceder a la tabla 'Estud_nacion' y filtrar por 'cve_estud'
    try:
        nacion = Estud_nacion.objects.get(cve_estud=estudiante.cve_estud)
        # Luego, acceder a la tabla 'Catanaci' y filtrar por 'cve_nacion' (suponiendo que 'nacion' contiene el registro que necesitas)
        pais = Catanaci.objects.get(cve_nacion=nacion.cve_nacion)
    except Estud_nacion.DoesNotExist:
        # Luego, acceder a la tabla 'Catanaci' y filtrar por 'cve_nacion' (suponiendo que 'nacion' contiene el registro que necesitas)
        pais = ''

    # recuperar los cursos del estudiante
    capcursos =  Sinsevi.objects.filter(cve_estud=cve_estud) # se envia el objeto a html

    render_data = {
        'estudiante': estudiante, 'programa': programa, 'capcursos': capcursos, 'periodo': periodo, 'anio': anio, 'consejero': consejero,
        'entidad_beca': entidad_beca, 'pais': pais, 'consejero_orientador': consejero_orientador, 'cvu':cvu }

    return render(request, 'guardar_boleta.html', render_data)


def actualizar_cvu(request):
    #print('YA VAMOS A ACTUALIZAR CVU')
    if request.method == 'POST' and 'cvu' in request.POST:
        nuevo_cvu = request.POST['cvu']
        #print(nuevo_cvu)
        # Asume que hay algún identificador único (como el ID) para identificar el registro específico
        # Si no lo hay, deberás ajustar esta parte según tu lógica de negocio.
        usuario_id = request.session.get('usuario_id')
        estudiante = get_object_or_404(Estudian, id=usuario_id)
        #print('el estudiante es: ', estudiante.cve_estud)

        # Obtiene el objeto Becario que se va a actualizar
        becario = Becarios.objects.get(cve_estud=estudiante.cve_estud)

        # Actualiza el valor de cvu
        becario.cvu = nuevo_cvu
        becario.save()

        return JsonResponse({'success': 'CVU actualizado correctamente'}, status=200)

    return JsonResponse({'error': 'Se esperaba una solicitud POST con el parámetro "cvu"'}, status=400)

def recibir_archivo(request):
    if request.method == "POST" and request.FILES:
        print('si es post este arch')
        archivo = request.FILES["archivo"]
        nombre_archivo = archivo.name

        # Ruta donde se almacenarán los archivos (directorio 'AETA_2023' en el directorio de medios de Django)
        ruta_archivos = os.path.join("AETA_2023", nombre_archivo)

        # Guardar el archivo en el servidor
        with open(ruta_archivos, "wb") as destino:
            for chunk in archivo.chunks():
                destino.write(chunk)

        # Aquí puedes realizar otras operaciones con el archivo si es necesario

        return JsonResponse({"message": "El archivo se ha guardado correctamente."})

    return JsonResponse({"message": "No se ha recibido ningún archivo o el método de solicitud no es válido."})


def cursos_asistire(request):
    usuario_id = request.session.get('usuario_id')
    periodo = settings.PERIODO
    anio = settings.ANIO
    estudiante = get_object_or_404(Estudian, id=usuario_id)
    # valor de aeta

    if not usuario_id:
        return redirect('sinsevi:inicio_sesionE')

    try:
        estudiante.incrementar_cont_veces()
        if estudiante.cont_final >= 5:
            return redirect('sinsevi:inicio_sesionE')
    except Estudian.DoesNotExist:
        messages.error(request, 'El usuario no existe.')
        return redirect('sinsevi:inicio_sesionE')

    # recuperar datos del estudiate
    cve_program = estudiante.cve_program
    cve_estud = estudiante.cve_estud
    if cve_program == 'ECD':
        programa = get_object_or_404(CapcursappCoordinaciones, cve_program=cve_program)
        print('Es E C D: ', cve_program)
    elif cve_program == 'EST':
        programa = get_object_or_404(CapcursappCoordinaciones, cve_program='ECD')
        print('Es E S T: ', cve_program)
    else:
        programa = get_object_or_404(CapcursappCoordinaciones, cve_program=cve_program)
        print('Es normal ', cve_program)

    beca = Becarios.objects.filter(cve_estud=cve_estud).first()
    if beca is None:
        entidad_beca = ''
    else:
        entidad_beca = Catabeca.objects.filter(cve_becaria=beca.cve_becaria).first()
        # Filtra los registros de la tabla Estudiante_Consejero donde el campo cve_estud coincida con el valor de cve_estud.
    try:
        cvu = beca.cvu
    except:
        cvu = 0

    try:
        consejero_estudiante = estudiante_consejero.objects.get(cve_estud=cve_estud)
        consejero = Academic.objects.get(cve_academic=consejero_estudiante.cve_academic)
        consejero_orientador = 'PROFESOR(A) CONSEJERO'
    except estudiante_consejero.DoesNotExist:
        # buscamos en la tabla orientador
        consejero_estudiante = Orientador.objects.get(cve_estud=cve_estud)
        consejero = Academic.objects.get(cve_academic=consejero_estudiante.cve_academic)
        consejero_orientador = 'PROFESOR(A) ORIENTADOR(A)'

    # nacionalidad
    # Acceder a la tabla 'Estud_nacion' y filtrar por 'cve_estud'
    try:
        nacion = Estud_nacion.objects.get(cve_estud=estudiante.cve_estud)
        # Luego, acceder a la tabla 'Catanaci' y filtrar por 'cve_nacion' (suponiendo que 'nacion' contiene el registro que necesitas)
        pais = Catanaci.objects.get(cve_nacion=nacion.cve_nacion)
    except Estud_nacion.DoesNotExist:
        # Luego, acceder a la tabla 'Catanaci' y filtrar por 'cve_nacion' (suponiendo que 'nacion' contiene el registro que necesitas)
        pais = ''

    capcursos = Sinsevi.objects.filter(cve_estud=cve_estud)  # se envia el objeto a html

    render_data = {
        'estudiante': estudiante, 'programa': programa, 'capcursos': capcursos, 'periodo': periodo, 'anio': anio,
        'consejero_orientador': consejero_orientador, 'consejero':consejero,
        'entidad_beca': entidad_beca, 'pais': pais, 'cvu': cvu}

    return render(request, 'cursos_asistire.html', render_data)


# IMplementacion de envio de pdf
def generarPDF(request):
    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        estudiante = get_object_or_404(Estudian, id=usuario_id)

        # Verifica si el correo ya ha sido enviado
        if estudiante.cont_final > 0:
            messages.warning(request, 'El correo ya ha sido enviado anteriormente.')
            return redirect('sinsevi:cursos_asistire')

        consejero_estudiante = estudiante_consejero.objects.filter(cve_estud=estudiante.cve_estud).first()
        try:
            consejero = Academic.objects.filter(cve_academic=consejero_estudiante.cve_academic).first()
        except:
            # buscamos en la tabla orientador
            consejero_estudiante = Orientador.objects.get(cve_estud=estudiante.cve_estud)
            consejero = Academic.objects.get(cve_academic=consejero_estudiante.cve_academic)

        coordinacion = CapcursappCoordinaciones.objects.filter(cve_program=estudiante.cve_program).first()

        archivo_adjunto = request.FILES.get('pdf')
        # Envía el correo electrónico
        destinatario = ['rodriguez.rosales@colpos.mx']
        #destinatario = ['sinscripcolpos@gmail.com', estudiante.username, 'servacadmontecillo@colpos.mx', consejero.email, coordinacion.username, 'posgradosybecascm@colpos.mx']

        asunto = 'Boleta de preinscripción' + ' ' + str(estudiante.cve_estud) + ' ' + estudiante.nombres + ' ' + estudiante.apellidos
        periodo = settings.PERIODO
        mensaje = 'C O L E G I O   D E   P O S T G R A D U A D O S\n'
        mensaje += 'C A M P U S   M O N T E C I L L O\n\n'
        mensaje += 'Se adjunta documento PDF de la boleta de preinscripción para el periodo de ' + periodo +  ' del estudiante '  + estudiante.cve_program + '-' + str(estudiante.cve_estud) + '-'+ estudiante.nombres + ' ' + estudiante.apellidos
        mensaje += '\n\nATENTAMENTE\n\n'
        mensaje += 'SUBDIRECCIÓN DE EDUCACIÓN DEL CAMPUS MONTECILLO'
        mensaje_plano = strip_tags(mensaje)

        # Crear el objeto EmailMultiAlternatives
        email = EmailMultiAlternatives(
            asunto,
            str(mensaje_plano),
            'SINSEVI',
            destinatario
        )

        #crear nombre del archivo
        nombre_archivo = f'{estudiante.cve_program}-{estudiante.cve_estud}-{estudiante.nombres}_{estudiante.apellidos}-{settings.PERIODO}_{settings.ANIO}.pdf'
        archivo_adjunto.name = nombre_archivo

        sello_path = 'static/imagenes/sello_subedu.png'
        # Agrega el sello al PDF en memoria
        pdf_stream_con_sello = agregar_sello(archivo_adjunto.read(), sello_path)

        # Adjuntar el archivo PDF al correo electrónico
        email.attach(archivo_adjunto.name, pdf_stream_con_sello.read(), 'application/pdf')

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
            estudiante = Estudian.objects.get(id=estudiante.id)
            estudiante.incrementar_cont_final()
            messages.success(request, '¡Correo electrónico enviado correctamente!')
            # Redirige a la página 'cursos_guardados'
            return redirect('sinsevi:cursos_asistire')
        except smtplib.SMTPException as e:
            messages.success(request, '¡Correo electrónico no enviado, intente de nuevo!')
            return HttpResponse(f'Error al enviar el correo electrónico: {str(e)}')
    return HttpResponse('Error al generar el PDF')



def agregar_sello(pdf_stream, sello_path):
    # Crear un nuevo objeto PdfWriter
    pdf_writer = PdfWriter()

    # Crear un objeto PdfReader con el flujo del PDF original
    pdf_reader = PdfReader(BytesIO(pdf_stream))

    # Obtener la primera página del PDF original
    page = pdf_reader.pages[0]

    # Crear un nuevo objeto Canvas para el sello
    sello_canvas = canvas.Canvas(BytesIO())

    # Ajustar la posición y tamaño del sello
    sello_ancho = 3.7  # Ancho del sello en cm
    sello_alto = 4.5  # Alto del sello en cm
    sello_pos_x = float(page.mediabox.width) / 2 - sello_ancho * 28.35 / 2
    sello_pos_y = 120  # Posición en la parte baja del documento

    # Cargar el sello
    sello = Image.open(sello_path)

    # Guardar temporalmente la imagen Pillow en un archivo
    temp_sello_path = "static/imagenes/sello.png"  # Cambia la ruta a tu ubicación temporal
    sello.save(temp_sello_path)

    # Dibujar el sello en el Canvas con el parámetro mask
    sello_canvas.drawImage(temp_sello_path, sello_pos_x, sello_pos_y, width=sello_ancho * 28.35, height=sello_alto * 28.35, mask='auto')
    sello_canvas.save()

    # Fusionar la página original con el sello
    packet = BytesIO()
    can = canvas.Canvas(packet)
    can.drawImage(temp_sello_path, sello_pos_x, sello_pos_y, width=sello_ancho * 28.35, height=sello_alto * 28.35, mask='auto')
    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)

    existing_page = page
    new_page = new_pdf.pages[0]
    existing_page.merge_page(new_page)

    # Agregar la página modificada al escritor del nuevo PDF
    pdf_writer.add_page(existing_page)

    # Crear un nuevo flujo de salida para el PDF modificado
    output_stream = BytesIO()
    pdf_writer.write(output_stream)
    output_stream.seek(0)

    # Eliminar el archivo temporal
    os.remove(temp_sello_path)

    return output_stream