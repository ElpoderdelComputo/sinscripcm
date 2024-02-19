from django.contrib.auth.backends import ModelBackend
from sinsevi.models import Estudian

class EstudianBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            print('sinsevi: sorri, no miso')
            user = Estudian.objects.get(username=username)
            print('sinsevi: Simon, adelante man')
        except Estudian.DoesNotExist:
            print('sinsevi: Pasa al except, no hay ese user y por eso devuelve none')
            return None

        if user.check_password(password):
            print('sinsevi: Simon, adelante man')

            return user
        return None