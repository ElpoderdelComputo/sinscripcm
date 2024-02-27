import json
import os
import smtplib
from datetime import date
from urllib import request
from email.header import Header
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils.html import strip_tags
from SINSCRIP import settings
from capcursapp.models import Coordinaciones
from sinsevi.models import Estudian
import logging  # Importa el módulo de registro
logger = logging.getLogger(__name__)  # Configura el objeto logger
from django.core.serializers.json import DjangoJSONEncoder
# Create your views here.


def iniciar_sesion(request):
    # Cerrar sesión (antes de redireccionar)
    return render(request, 'inicio_cordins.html')

def logout_view(request):
    logout(request)
    return redirect('cordins:iniciar_sesion')

def verificar_credenciales(request):

    if settings.coordins_on == 0:
        messages.error(request, 'El sistema aún no está disponible.')
        return render(request, 'fuera_de_linea.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['usuario_id'] = user.id
            print('si se autentico mano', user.cve_program)
            return redirect('cordins:panel_posgrados')
        else:
            # Las credenciales son inválidas
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'inicio_cordins.html')
    else:
        return render(request, 'inicio_cordins.html')


def estudiante_to_dict(estudiante):

    return {
        'id': estudiante.id,
        'cve_estud': estudiante.cve_estud,
        'nombres': estudiante.nombres,
        'apellidos': estudiante.apellidos,
        'cve_campus': estudiante.cve_campus,
        'cve_institu': estudiante.cve_institu,
        'cve_program': estudiante.cve_program,
        'periingr': estudiante.periingr,
        'fechingr': estudiante.fechingr,
        'cve_sexo': estudiante.cve_sexo,
        'e_mail': estudiante.e_mail,
        'e_mailcp': estudiante.e_mailcp,
        'aeta': estudiante.aeta,
        'consejop': estudiante.consejop,
        'username': estudiante.username,
        'password': estudiante.password,
        'niveestu': estudiante.niveestu,
        'cont_veces': estudiante.cont_veces,
        'cont_final': estudiante.cont_final,
    }


def custom_json_serializer(obj):
    if isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    raise TypeError("Object of type '{}' is not JSON serializable".format(type(obj).__name__))


def panel_posgrados(request):
    usuario_id = request.session.get('usuario_id')

    try:
        usuario = Coordinaciones.objects.get(id=usuario_id)
    except Coordinaciones.DoesNotExist:
        # Si el usuario no existe, redirige al inicio de sesión
        messages.error(request, 'Usuario o contraseña incorrectos.')
        return redirect('cordins:iniciar_sesion')

    periodo = settings.PERIODO
    anio = settings.ANIO
    periodo_aeta = settings.PERIODO_AETA
    anio_aeta = settings.ANIO_AETA
    fn_ingreso = settings.FN_INGRESO

    estudiantes = Estudian.objects.filter(cve_program=usuario.cve_program)
    data = [{'cve_estud': est.cve_estud, 'niveestu': est.niveestu, 'nombres': est.nombres,
             'apellidos': est.apellidos, 'fechingr': est.fechingr, 'consejop': est.consejop,
             'aeta': est.aeta} for est in estudiantes]

    return render(request, 'panel_posgra.html',
                  {'usuario': usuario, 'periodo': periodo, 'anio': anio, 'data': data, 'periodo_aeta': periodo_aeta,
                   'anio_aeta':anio_aeta, 'fn_ingreso':fn_ingreso })


def actualizar_checkbox(request):
    if request.method == 'POST':
        matricula = request.POST.get('cve_estud')
        estudiante = Estudian.objects.filter(cve_estud=matricula).first()
        print(estudiante.nombres, estudiante.apellidos)

        # Cambiar el valor del campo checkbox
        estudiante.aeta = not estudiante.aeta
        estudiante.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})


def recibir_archivo(request):
    print('Recibieidno pdf')
    if request.method == "POST":
        cve_estud = request.POST.get('cve_estud')
        cve_program = request.POST.get('cve_program')

        print('Estudiante: ', cve_estud,' ', cve_program)

        #archivo = request.FILES["archivo"]
        archivo = request.FILES["pdf"]
        periodo = settings.PERIODO_AETA
        anio = settings.ANIO

        nombre_archivo = str(cve_program) + str(cve_estud) + 'AETA' + str(periodo) + str(anio) + '.pdf'

        #nombre_archivo = archivo.name
        if archivo.size > 2097152:
            print('pesa mas de 2 mb')
            mensage = 'El documento PDF debe pesar menos de 2 MB'
            return JsonResponse({"message": mensage})

        # Ruta donde se almacenarán los archivos (directorio 'boletas_2023' en el directorio de medios de Django)
        ruta_archivos = os.path.join("AETA_2023", nombre_archivo)

        # Guardar el archivo en el servidor
        with open(ruta_archivos, "wb") as destino:
            for chunk in archivo.chunks():
                destino.write(chunk)

        # Aquí puedes realizar otras operaciones con el archivo si es necesario
        estudiante = Estudian.objects.get(cve_estud=cve_estud, cve_program=cve_program)
        estudiante.aeta = True  # O asigna el valor que corresponda
        estudiante.save()  # Guarda los cambios en la base de datos

        #correo_consejero, correo_corrd
        print('Vamos a enviar el correo')
        enviar_aviso(estudiante.cve_estud)
        print('FIn de Proceso email')

        mensage = 'El Acta de evaluación se ha guardado para: ' + estudiante.nombres + ' ' + estudiante.apellidos

        return JsonResponse({"message": mensage})
    print('No es post Man')

    return JsonResponse({"message": "No se ha recibido ningún archivo o el método de solicitud no es válido."})



def  enviar_aviso(cve_estud):
    print('ejecutando enviar_aviso')
    estudiante = get_object_or_404(Estudian, cve_estud=cve_estud)

    if estudiante.cve_program == 'ECD':
        estudiante.cve_program = 'EST'

    coordinacion = Coordinaciones.objects.filter(cve_program=estudiante.cve_program).first()

    # Envía el correo electrónico al estudiante, consejero y coordinacón
    destinatario = [estudiante.username, coordinacion.username]
    #destinatario = ['rodriguez.rosales@colpos.mx']
    # Codificar destinatarios
    destinatario_encoded = [Header(d, 'utf-8').encode() for d in destinatario]

    #destinatario = ['sinscripcolpos@gmail.com', estudiante.e_mailcp, 'servacadmontecillo@colpos.mx', consejero.email, coordinacion.username, 'posgradosybecas@colpos.mx']
    print('avisando a: ', estudiante.nombres)
    asunto = 'Mensaje del Sistema de Inscripciones en Linea'
    periodo = settings.PERIODO
    anio = settings.ANIO
    mensaje = 'Estimad@: ' + estudiante.nombres + ' ' + estudiante.apellidos
    mensaje += '\n\nLa coordinacion de su posgrado ha revisado su Acta de Evaluacion de Trabajo Académico\n'
    mensaje += 'Por lo que le informamos que puede acceder al sistema de inscripciones en linea (SINSEVI)\n'
    mensaje += 'para realizar el proceso de inscripciones del periodo de ' + periodo + ' ' + str(anio) + '.\n'
    mensaje += 'URL Interno: http://10.0.0.90:9000/sinsevi/\n'
    mensaje += 'URL Externo: http://200.23.26.90:9000/sinsevi/ \n'
    mensaje += '\n\nATENTAMENTE\n\n'
    mensaje += 'SUBDIRECCIÓN DE EDUCACIÓN\n'
    mensaje += 'CAMPUS MONTECILLO'
    mensaje_plano = strip_tags(mensaje)

    # Crear el objeto EmailMultiAlternatives
    email = EmailMultiAlternatives(
        asunto,
        str(mensaje_plano),
        'SINSEVI Campus Montecillo',
        destinatario_encoded # Usar destinatarios codificados
    )

    # Envía el correo electrónico utilizando SMTP
    try:
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_usuario = 'sinscripcolpos@gmail.com'
        smtp_password = 'murvdxcfnfroschr'  # Asegúrate de utilizar las credenciales correctas
        smtp = smtplib.SMTP(smtp_server, smtp_port)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(smtp_usuario, smtp_password)
        smtp.sendmail(smtp_usuario, destinatario, email.message().as_bytes())

        smtp.quit()
        print('FIn de enviar_aviso')

        # Después de procesar el archivo con éxito
        return HttpResponse('Archivo recibido correctamente.')

    except smtplib.SMTPException as e:
        # Registra el error en un archivo de registro o utiliza una biblioteca de registro
        logger.error(f'Error al enviar el correo electrónico: {str(e)}')
        messages.success(request, '¡Correo electrónico no enviado, intente de nuevo!')
        return HttpResponse(f'Error al enviar el correo electrónico: {str(e)}')





