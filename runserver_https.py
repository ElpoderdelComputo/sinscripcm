'''import os
from django.core.management import execute_from_command_line

os.environ['DJANGO_SETTINGS_MODULE'] = 'sinscrip.settings'  # Reemplaza 'tu_proyecto' con el nombre de tu proyecto

args = ['manage.py', 'runserver', '0.0.0.0:9000']

# Configurar la ruta a los archivos de certificado SSL
ssl_cert = '/etc/letsencrypt/live/repca.colpos.mx/fullchain.pem'  # Ruta al certificado
ssl_key = '/etc/letsencrypt/live/repca.colpos.mx/privkey.pem'  # Ruta a la clave privada

os.environ['HTTPS_CERTIFICATE'] = ssl_cert
os.environ['HTTPS_KEY'] = ssl_key

execute_from_command_line(args)'''
