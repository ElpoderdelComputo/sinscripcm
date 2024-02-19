from django import forms
from sinsevi.models import Asistira, Sinsevi, Becarios, AltaBaja


class AsistiraForm(forms.ModelForm):
    class Meta:
        model = Asistira
        #solo se listan los campos que se rellenan desde formulario.
        fields = ['cve_curso']


class SinseviForm(forms.ModelForm):
    class Meta:
        model = Sinsevi
        #solo se listan los campos que se rellenan desde formulario.
        fields = ['cve_curso', 'cve_academic']


class BecariosForm(forms.ModelForm):
    class Meta:
        model = Becarios
        #solo se listan los campos que se rellenan desde formulario.
        fields = ['cvu']

class Alta_bajaForm(forms.ModelForm):
    class Meta:
        model = AltaBaja
        #solo se listan los campos que se rellenan desde formulario.
        fields = ['cve_curso', 'cve_academic']

