"""
WSGI config for SINSCRIP project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SINSCRIP.settings')

'''# Configurar las variables de entorno para los certificados SSL
os.environ['HTTPS_CERTIFICATE'] = '/etc/letsencrypt/live/repca.colpos.mx/fullchain.pem'
os.environ['HTTPS_KEY'] = '/etc/letsencrypt/live/repca.colpos.mx/privkey.pem'''


application = get_wsgi_application()
