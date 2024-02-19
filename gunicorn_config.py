bind = '10.0.0.90:9000'  # Escucha en la IP interna en el puerto 9000
#bind = '0.0.0.0:9000'  # Escucha en la IP interna en el puerto 9000
workers = 4  # Número de trabajadores Gunicorn
pidfile = '/tmp/sinscrip_gunicorn.pid'
daemon = True
timeout = 60
# Configuración de acceso y errores
loglevel = 'info'  # Nivel de registro
accesslog = '/home/educm/SINSCRIP/sinscrip/sinscrip_logs/access.log'
errorlog = '/home/educm/SINSCRIP/sinscrip/sinscrip_logs/error.log'
