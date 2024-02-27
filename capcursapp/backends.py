from django.contrib.auth.backends import ModelBackend
from capcursapp.models import Coordinaciones

class CoordinacionesBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Coordinaciones.objects.get(username=username)
        except Coordinaciones.DoesNotExist:
            print('capcursapp: Pasa al except, no hay ese user y por eso devuelve none')
            return None

        if user.check_password(password):
            return user
        return None

