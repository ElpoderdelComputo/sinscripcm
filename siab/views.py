import os
from io import BytesIO
import smtplib
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login
import json
from django.utils import timezone
from django.utils.html import strip_tags
from SINSCRIP import settings
from capcursapp.models import Academic
from sinsevi.forms import AsistiraForm, SinseviForm, Alta_bajaForm
from sinsevi.models import CapcursappCoordinaciones, estudiante_consejero, Capcurs, Catacurs, Becarios, Asistira, \
    Catabeca, \
    Imparegu, Estudian, Sinsevi, Estud_nacion, Catanaci, AltaBaja, Orientador
from django.http import JsonResponse, HttpResponse
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from PIL import Image



# Create your views here.
def inicio_siayb(request):
    # Cerrar sesión (antes de redireccionar)
    return render(request, 'inicio_sesionsiayb.html')


def logout_view(request):
    logout(request)
    return redirect('siab:inicio_siayb')


def verificar_credenciale_siayb(request):
    # Verificar si el sistema esta en linea
    if settings.siayb_on == 0:
        messages.error(request, 'El sistema aún no está disponible.')
        return render(request, 'fuera_de_linea.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print('usuario y pass: ',username, password)
        try:
            user = Estudian.objects.get(username=username)
            print('Inicio sesion: ', str(user))
            if user.check_password(password):
                # Las credenciales son válidas
                login(request, user, backend='sinsevi.backends.EstudianBackend')
                request.session['usuario_id'] = user.id
                print('El usuario es valido: ', user.id)
                print('simon, si esta bien')
                return redirect('siab:mis_cursos_siayb')
            else:
                # Las credenciales son inválidas
                print('Las credenciales son inválidas')
                messages.error(request, 'Usuario o contraseña incorrectos.')
                return render(request, 'inicio_sesionsiayb.html')
        except Estudian.DoesNotExist:
            # El usuario no existe
            print('EL usuario no existe bro')
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'inicio_sesionsiayb.html')
    else:
        print('no es post')
        return render(request, 'inicio_sesionsiayb.html')

def fuera_de_linea(request):
    return render(request, 'fuera_de_linea.html')

def mis_cursos_siayb(request):
    usuario_id = request.session.get('usuario_id')

    periodo = settings.PERIODO
    anio = settings.ANIO
    estudiante = get_object_or_404(Estudian, id=usuario_id)
    # Verifica si el correo ya ha sido enviado
    if estudiante.email_ayb > 0:
        return redirect('siab:altas_bajas')

    # Verifica si el estudiante se inscribió
    if estudiante.cont_final == 0:
        print('No se inscribio')
        messages.error(request, 'No finalizó el proceso de Inscripciónes')
        return redirect('siab:altas_bajas')

    try:
        estudiante.incrementar_cont_veces()
        if estudiante.cont_final >= 5:  # cambiar de 5 a1
            return redirect('siab:inicio_siayb')
    except Estudian.DoesNotExist:
        messages.error(request, 'El usuario no existe.')
        return redirect('siab:inicio_siayb')

    #recuperar datos del estudiate
    cve_estud = estudiante.cve_estud
    cve_program = estudiante.cve_program

    programa = get_object_or_404(CapcursappCoordinaciones, cve_program=cve_program)

    try:
        beca = get_object_or_404(Becarios, cve_estud=cve_estud)
        print('Si Beca: ', beca.cve_becaria, beca.cvu)
        cvu = beca.cvu
        entidad_beca = get_object_or_404(Catabeca, cve_becaria=beca.cve_becaria)
    except Becarios.DoesNotExist:
        print('No tiene beca')
        entidad_beca = ''
        cvu = 0

    # Filtra los registros de la tabla Consejo donde el campo cve_estud coincida con el valor de cve_estud.
    fecha_nuevo_ingr = settings.FN_INGRESO

    try:
        consejero_estudiante = estudiante_consejero.objects.get(cve_estud=cve_estud, orden=1)
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
        print(curso.credima)
        if curso.cve_curso in [str(cve_program) + '680', str(cve_program) + '681', str(cve_program) + '682']:
            cred_seminarios += curso.credima
        elif curso.cve_curso == str(cve_program) + '690':
            cred_inv += curso.credima
        else:
            cred_regular += curso.credima

    cred_inv1 = cred_inv - cred_regular
    if cred_inv1 <= 0:
        cred_inv1 = 0
    total = cred_regular + cred_seminarios + cred_inv1
    suma_creditos = {
        'cred_seminarios': cred_seminarios,
        'cred_inv': cred_inv1,
        'cred_regular': cred_regular,
        'total': total,
    }

    config = {
        'periodo': settings.PERIODO,
        'anio': settings.ANIO,
        'flimite': settings.FECHA_LIMITE
    }
    # Obtén la cantidad de objetos en la variable movimientos
    movimientos = AltaBaja.objects.filter(cve_estud=cve_estud)  # se envia el objeto a html
    cantidad_movimientos = movimientos.count()

    render_data = {
        'estudiante': estudiante, 'programa': programa, 'capcursos': capcursos, 'config': config, 'consejero': consejero,
        'entidad_beca': entidad_beca, 'pais': pais , 'suma_creditos': suma_creditos, 'cvu': cvu, 'cantidad_movimientos':cantidad_movimientos}

    return render(request, 'mis_cursos_siayb.html', render_data)


def curso_to_dict(curso):
    return {
        'id': curso.id,
        'nombre': curso.nombre,
        'cve_curso': curso.cve_curso,
        'cve_academic': curso.cve_academic_id
    }
from django.urls import reverse

# APP SIAYB
def selecciona_cursoAyB(request):
    # Obtener todos los registros de la tabla CAPCURS
    print('Se ha dado el click man')
    usuario_id = request.session.get('usuario_id')
    usuario = Estudian.objects.get(id=usuario_id)

    # Verifica si el correo ya ha sido enviado
    if usuario.email_ayb > 0:
        return redirect('siab:altas_bajas')

    capcursos = Sinsevi.objects.filter(cve_estud=usuario.cve_estud)  # Filtrar objetos
    capcursos_count = capcursos.count()
    if capcursos_count == 6:
        mensaje = f"Usted tiene {capcursos_count} cursos. Sólo puede agregar hasta 6 cursos en el sistema."
        url = reverse('siab:mis_cursos_siayb')
        return redirect(f"{url}?mensaje={mensaje}")

    # Obtén la cantidad de objetos en la variable movimientos
    movimientos = AltaBaja.objects.filter(cve_estud=usuario.cve_estud)  # se envia el objeto a html
    cantidad_movimientos = movimientos.count()
    if cantidad_movimientos == 7:
        return redirect('siab:mis_cursos_siayb')

    los_cursos = Capcurs.objects.all()
    loscursos = los_cursos.order_by('cve_curso')
    clave = ['AEC', 'BOT', 'COA', 'DES', 'ECO', 'EDA', 'ENT', 'ECD', 'FIV', 'FIT', 'FOR', 'FRU', 'GAN', 'GEN', 'HID',
             'IDI', 'SEM']
    valor = ['AGROECOLOGÍA Y SUSTENTABILIDAD', 'BOTANICA', 'CÓMPUTO APLICADO', 'DESARROLLO RURAL', 'ECONOMÍA',
             'EDAFOLOGÍA', 'ENTOMOLOGÍA Y ACAROLOGIA', 'ESTADISTICA Y CIENCIA DE DATOS', 'FISIOLOGIA VEGETAL',
             'FITOPATOLOGIA',
             'CIENCIAS FORESTALES', 'FRUTICULTURA', 'GANADERIA', 'GENETICA', 'HIDROCIENCIAS', 'IDIOMAS',
             'PRODUCCIÓN DE SEMILLAS']

    programas = dict(zip(clave, valor))

    cursos_por_programa = {}
    for programa in programas:
        # Obtener los cursos que pertenecen al programa actual
        cursos = Capcurs.objects.filter(cve_program=programa).order_by('cve_curso')
        cursos_por_programa[programa] = [curso_to_dict(curso) for curso in cursos]
    cursos_por_programa_json = json.dumps(cursos_por_programa)

    return render(request, 'selecciona_cursoAyB.html', {
        'usuario': usuario,
        'loscursos': loscursos,
        'programas': programas,
        'cursos_por_programa_json': cursos_por_programa_json
    })


def buscar_curso_ayb(request):
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
            # print('la data es: ', data)
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


def revisa_altas_bajas(cve_estud, cve_curso, cve_academic):
    print('revisamos la tabla')
    try:
        # Obtener los registros con alta_baja = 0
        registros_baja = AltaBaja.objects.filter(cve_estud=cve_estud, cve_academic=cve_academic, cve_curso=cve_curso, alta_baja=0)

        if registros_baja.exists():
            # Verificar si existe un registro con la misma clave y alta_baja = 1
            registro_alta = AltaBaja.objects.filter(cve_estud=cve_estud, cve_academic=cve_academic, cve_curso=cve_curso, alta_baja=1)

            if registro_alta.exists():
                # Eliminar ambos registros
                registros_baja.delete()
                registro_alta.delete()
                message = 'Registros eliminados con éxito.'
            else:
                message = 'No se encontró un registro con alta_baja = 1.'
        else:
            message = 'No hay registros con alta_baja = 0 para eliminar.'

        response_data = {'success': True, 'message': message}
    except Exception as e:
        response_data = {'success': False, 'message': str(e)}

    return JsonResponse(response_data)


def crea_asistiraAyB(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Estudian.objects.get(id=usuario_id)
    if usuario.email_ayb > 0:
        messages.warning(request, 'El correo ya ha sido enviado anteriormente.')
        return redirect('siab:altas_bajas')

    if request.method == 'POST':
        form_asistira = AsistiraForm(request.POST)
        form_sinsevi = SinseviForm(request.POST)
        form_alta_baja = Alta_bajaForm(request.POST)

        if form_asistira.is_valid() and form_sinsevi.is_valid() and form_alta_baja.is_valid():
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

                    print('De capcursapp: ->', micurso.id, micurso.cve_curso, micurso.cve_academic_id)
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

                    alta_baja = AltaBaja()
                    alta_baja.cve_estud = usuario.cve_estud
                    alta_baja.cve_curso = cve_curso
                    alta_baja.nombre = micurso.nombre
                    alta_baja.cve_academic = micurso.cve_academic_id
                    alta_baja.nom_academic = micurso.nom_academic
                    alta_baja.apellidos = micurso.apellidos
                    alta_baja.gpo_670 = catacurs.gpo_670
                    alta_baja.fech_mov = timezone.now().date()  # Establecer la fecha actual
                    alta_baja.alta_baja = 1 #alta de curso
                    alta_baja.save()

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


def crea_asistira690(request):
    # Obtener el ID de usuario de la sesión
    usuario_id = request.session.get('usuario_id')
    usuario = Estudian.objects.get(id=usuario_id)
    print('El usuario: ', usuario.cve_estud)

    if usuario.email_ayb > 0:
        return redirect('siab:altas_bajas')

    capcursos = Sinsevi.objects.filter(cve_estud=usuario.cve_estud)  # Filtrar objetos
    capcursos_count = capcursos.count()
    if capcursos_count == 6:
        response_data = {'success': True, 'message': 'Sólo puede agregar hasta 6 cursos en el sistema.'}
        return JsonResponse(response_data)

    # Obtén la cantidad de objetos en la variable movimientos
    movimientos = AltaBaja.objects.filter(cve_estud=usuario.cve_estud)  # se envia el objeto a html
    cantidad_movimientos = movimientos.count()
    if cantidad_movimientos == 6:
        response_data = {'success': True, 'message': 'Sólo puede realizar 6 movimientos en el sistema.'}
        return JsonResponse(response_data)

    try:
        # Calcular el código del curso
        if usuario.cve_program == 'ECD':
            codigo_690 = 'EST690'
        elif usuario.niveestu == 'DOC - INV':
            codigo_690 = 'DMI690'
        else:
            codigo_690 = usuario.cve_program + '690'

        # Verificar si el curso ya existe en la tabla Asistira
        if Asistira.objects.filter(cve_estud=usuario.cve_estud, cve_curso=codigo_690).exists():
            # El curso ya existe, enviar un mensaje de error.
            print('Ya existe')
            response_data = {'success': False, 'message': 'INVESTIGACIÓN ya ha sido agregado.'}
        else:
            # El curso no existe, crearlo.
            # Obtener datos del investigador
            consejero_estudiante = estudiante_consejero.objects.filter(cve_estud=usuario.cve_estud).first()
            investigador = Imparegu.objects.filter(cve_curso=codigo_690,
                                                   cve_academic=consejero_estudiante.cve_academic).first()
            print('EL investigador es: ', investigador.cve_academic)
            # Obtener datos del curso en Catacurs
            catacurs = Catacurs.objects.filter(cve_curso=codigo_690, gpo_670=investigador.gpo_670, credima=9).first()
            print('Este es el curso Y GPO: ', catacurs.cve_curso, catacurs.gpo_670)

            if catacurs is None:
                # Manejar el caso en que no se encuentre el curso en Catacurs
                response_data = {'success': False, 'message': 'Curso no encontrado en Catacurs.'}
            else:

                if investigador is None:
                    # Manejar el caso en que no se encuentre el investigador
                    response_data = {'success': False, 'message': 'Investigador no encontrado.'}
                else:
                    print('La creacion de estos registros')
                    # Crear registro Asistira nuevo
                    asistira = Asistira.objects.create(
                        cve_estud=usuario.cve_estud,
                        cve_curso=codigo_690,
                        gpo_670=investigador.gpo_670,
                        califica=0,
                        creditos=catacurs.credima,
                        periodo=settings.PERIODO,
                        agno=settings.ANIO,
                        observa='PEND.',  # valor por defecto
                        registro='1753-01-01',
                        per_vi_cur=catacurs.periodo,
                        ano_vi_cur=catacurs.agno,
                        no_periodo=settings.NO_PERIODO,  # valor por defecto primavera = 1 verano y otoño: 2,3
                        #isevaluated=0  # cambiara a 1 cuando se haya evaluado
                    )

                    # Obtener datos del profesor
                    profesor = Academic.objects.filter(cve_academic=investigador.cve_academic).first()

                    # Crear registro Sinsevi
                    sinsevi = Sinsevi.objects.create(
                        cve_estud=usuario.cve_estud,
                        cve_curso=codigo_690,
                        nombre=catacurs.nombre,
                        credimi=catacurs.credimi,
                        credima=catacurs.credima,
                        cve_academic=investigador.cve_academic,
                        nom_academic=profesor.nombres,
                        apellidos=profesor.apellidos,
                        gpo_670=investigador.gpo_670,
                    )
                    # Agregar mensaje de éxito

                    # Crear registro Alta_baja
                    alta_baja = AltaBaja.objects.create(
                        cve_estud=usuario.cve_estud,
                        cve_curso=codigo_690,
                        nombre=catacurs.nombre,
                        cve_academic=investigador.cve_academic,
                        nom_academic=profesor.nombres,
                        apellidos=profesor.apellidos,
                        gpo_670=investigador.gpo_670,
                        fech_mov=timezone.now().date(),  # Establecer la fecha actual
                        alta_baja=1,  #alta de curso
                    )
                    revisa_altas_bajas(usuario.cve_estud, codigo_690, investigador.cve_academic)

                    response_data = {'success': True, 'message': 'INVESTIGACIÓN se ha agregado exitosamente.'}
    except Estudian.DoesNotExist:
        # Manejar el caso en que el usuario no existe
        response_data = {'success': False, 'message': 'Usuario no encontrado.'}
    return JsonResponse(response_data)


def elimina_uncurso(request, id_sinsevi):
    usuario_id = request.session.get('usuario_id')
    estudiante = Estudian.objects.get(id=usuario_id)
    print('se ha dado click a eliminar id: ', id_sinsevi)
    elcurso = Sinsevi.objects.filter(id_sinsevi=id_sinsevi).first()

    asistira = Asistira.objects.get(cve_estud=estudiante.cve_estud, cve_curso=elcurso.cve_curso)
    if estudiante.email_ayb > 0:
        return redirect('siab:altas_bajas')


    # Crear registro Alta_baja
    alta_baja = AltaBaja.objects.create(
        cve_estud=estudiante.cve_estud,
        cve_curso=elcurso.cve_curso,
        nombre= elcurso.nombre,
        cve_academic=elcurso.cve_academic,
        nom_academic=elcurso.nom_academic,
        apellidos=elcurso.apellidos,
        gpo_670=elcurso.gpo_670,
        fech_mov=timezone.now().date(),  # Establecer la fecha actual
        alta_baja=0, # baja de un curso
    )
    revisa_altas_bajas(estudiante.cve_estud, elcurso.cve_curso, elcurso.cve_academic)

    # Eliminar registros
    elcurso.delete()
    asistira.delete()
    messages.success(request, 'Curso eliminado satisfactoriamente')

    return redirect('siab:mis_cursos_siayb')

def elimina_inv_690(request, id_curso):
    usuario_id = request.session.get('usuario_id')
    estudiante = Estudian.objects.get(id=usuario_id)
    cve_program = estudiante.cve_program
    estudiante = estudiante.cve_estud
    if estudiante.email_ayb > 0:
        return redirect('siab:altas_bajas')
    programa = get_object_or_404(CapcursappCoordinaciones, cve_program=cve_program)

    # Obtener datos del investigador
    consejero_estudiante = estudiante_consejero.objects.filter(cve_estud=estudiante).first()
    investigador = Imparegu.objects.filter(cve_curso=cve_program, cve_academic=consejero_estudiante.cve_academic).first()
    print('EL profe es: ', investigador.cve_academic)

    # Obtener datos del profesor
    profesor = Academic.objects.filter(cve_academic=investigador.cve_academic).first()

    asistira = Asistira.objects.get(id=id_curso)  # obtengo el curso en asistira
    print('Tonces eliminar: ', asistira.cve_curso)
    # Crear registro Alta_baja
    alta_baja = AltaBaja.objects.create(
        cve_estud=estudiante.cve_estud,
        cve_curso= asistira.cve_curso,
        cve_academic=profesor.cve_academic,
        nom_academic=profesor.nombres,
        apellidos=profesor.apellidos,
        gpo_670=investigador.gpo_670,
        fech_mov=timezone.now().date(),  # Establecer la fecha actual
        alta_baja=0, #baja de investigacion
    )
    revisa_altas_bajas(estudiante.cve_estud, asistira.cve_curso, profesor.cve_academic)
    # El curso no se encontró en capcursapp, enviar mensaje de error
    asistira.delete()  # Elimina todos los registros de la tabla asistira
    messages.success(request, 'Curso eliminado satisfactoriamente')
    return redirect('siab:mis_cursos_siayb')


def guardar_boletayb(request):
    usuario_id = request.session.get('usuario_id')
    periodo = settings.PERIODO
    anio = settings.ANIO
    estudiante = get_object_or_404(Estudian, id=usuario_id)
    # valor de aeta
    if estudiante.email_ayb > 0:
        return redirect('siab:altas_bajas')

    try:
        estudiante.incrementar_cont_veces()
        if estudiante.cont_final >= 5:
            return redirect('sinsevi:inicio_sesionE')
    except Estudian.DoesNotExist:
        messages.error(request, 'El usuario no existe.')
        return redirect('sinsevi:inicio_sesionE')

    # recuperar datos del estudiate
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
        entidad_beca = ''
    else:
        entidad_beca = Catabeca.objects.filter(cve_becaria=beca.cve_becaria).first()

    try:
        cvu = beca.cvu
    except:
        cvu = ''

    # Filtra los registros de la tabla Consejo donde el campo cve_estud coincida con el valor de cve_estud.
    fecha_nuevo_ingr = settings.FN_INGRESO
    try:
        consejero_estudiante = estudiante_consejero.objects.get(cve_estud=cve_estud)
        consejero = Academic.objects.get(cve_academic=consejero_estudiante.cve_academic)
        consejero_orientador = 'PROFESOR(A) CONSEJERO'
    except Academic.DoesNotExist:
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

        # recuperar los cursos del estudiante
    capcursos = Sinsevi.objects.filter(cve_estud=cve_estud)  # se envia el objeto a html
    movimientos = AltaBaja.objects.filter(cve_estud=cve_estud)  # se envia el objeto a html
    # Obtén la primera fecha de movimiento (si existe)
    fecha_ayb = movimientos.first().fech_mov if movimientos.exists() else None

    render_data = {
        'estudiante': estudiante, 'programa': programa, 'capcursos': capcursos, 'movimientos': movimientos,'periodo': periodo, 'anio': anio,
        'consejero': consejero, 'entidad_beca': entidad_beca, 'pais': pais, 'consejero_orientador': consejero_orientador, 'cvu': cvu, 'fecha_ayb':fecha_ayb}

    return render(request, 'guardar_enviarayb.html', render_data)

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


def altas_bajas(request):
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
        # Filtra los registros de la tabla consejo donde el campo cve_estud coincida con el valor de cve_estud.
    try:
        cvu = beca.cvu
    except:
        cvu = 0

    try:
        consejero_estudiante = estudiante_consejero.objects.get(cve_estud=cve_estud)
        consejero = Academic.objects.get(cve_academic=consejero_estudiante.cve_academic)
        consejero_orientador = 'PROFESOR(A) CONSEJERO'
    except Academic.DoesNotExist:
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

    capcursos = Sinsevi.objects.filter(cve_estud=cve_estud)
    movimientos = AltaBaja.objects.filter(cve_estud=cve_estud)  # se envia el objeto a html

    # Obtén la primera fecha de movimiento (si existe)
    fecha_ayb = movimientos.first().fech_mov if movimientos.exists() else None

    render_data = {
        'estudiante': estudiante, 'programa': programa, 'movimientos': movimientos, 'fecha_ayb':fecha_ayb, 'periodo': periodo, 'anio': anio,
        'consejero_orientador': consejero_orientador, 'consejero':consejero, 'capcursos':capcursos,
        'entidad_beca': entidad_beca, 'pais': pais, 'cvu': cvu}

    return render(request, 'altas_bajas.html', render_data)


def generarPDF(request):
    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        estudiante = get_object_or_404(Estudian, id=usuario_id)

        # Verifica si el correo ya ha sido enviado
        if estudiante.email_ayb > 0:
            return redirect('siab:altas_bajas')

        try:
            consejero_estudiante = estudiante_consejero.objects.filter(cve_estud=estudiante.cve_estud).first()
            consejero = Academic.objects.filter(cve_academic=consejero_estudiante.cve_academic).first()
        except estudiante_consejero.DoesNotExist:
            consejero_estudiante = Orientador.objects.get(cve_estud=estudiante.cve_estud)
            consejero = Academic.objects.get(cve_academic=consejero_estudiante.cve_academic)

        coordinacion = CapcursappCoordinaciones.objects.filter(cve_program=estudiante.cve_program).first()

        archivo_adjunto = request.FILES.get('pdf')

        sello_path = 'static/imagenes/sello_subedu.png'
        # Agrega el sello al PDF en memoria
        pdf_stream_con_sello = agregar_sello(archivo_adjunto.read(), sello_path)

        #crear nombre del archivo
        nombre_archivo = (
            f'{estudiante.cve_program}_AyB_{estudiante.cve_estud}-{estudiante.nombres}_{estudiante.apellidos}'
            f'-{settings.PERIODO}_{settings.ANIO}.pdf')

        archivo_adjunto.name = nombre_archivo

        # Guardar el archivo PDF con sello en disco
        ruta_archivos = os.path.join("ALTASYBAJAS", nombre_archivo)

        with open(ruta_archivos, "wb") as destino:
            destino.write(pdf_stream_con_sello.read())

        # Envía el correo electrónico
        #destinatario = ['rodriguez.rosales@colpos.mx']
        destinatario = [estudiante.username, 'servacadmontecillo@colpos.mx',
                        consejero.email, coordinacion.username, 'posgradosybecascm@colpos.mx']

        asunto = 'Boleta de Altas y Bajas' + ' ' + str(
            estudiante.cve_estud) + ' ' + estudiante.nombres + ' ' + estudiante.apellidos
        periodo = settings.PERIODO
        anio = settings.ANIO
        mensaje = 'ESTIMADOS: \n\n'
        mensaje += ('Se adjunta documento PDF de la boleta de ALTAS Y BAJAS para el periodo de ' + periodo + str(anio) +
                    '\ndel estudiante ' + estudiante.cve_program + '-' + str(
                    estudiante.cve_estud) + '-' + estudiante.nombres + ' ' + estudiante.apellidos + '.')
        mensaje += '\n\nSe incluyen los movimientos de altas y bajas asi como la inscripción final.'
        mensaje += '\n\nAtentamente,\n\n'
        mensaje += 'SUBDIRECCIÓN DE EDUCACIÓN\n'
        mensaje += 'CAMPUS MONTECILLO'
        mensaje_plano = strip_tags(mensaje)

        # Crear el objeto EmailMultiAlternatives
        email = EmailMultiAlternatives(
            asunto,
            str(mensaje_plano),
            'SIAB - CAMPUS MONTECILLO',
            destinatario
        )

        # Adjuntar el archivo PDF al correo electrónico
        # email.attach(archivo_adjunto.name, pdf_stream_con_sello.read(), 'application/pdf')
        with open(ruta_archivos, 'rb') as adjunto:
            email.attach(nombre_archivo, adjunto.read(), 'application/pdf')

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
            estudiante.incrementar_email_ayb()
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
