from django.shortcuts import render
from django.conf import settings

def panel_control(request):
    config = {
        'periodo': settings.PERIODO,
        'anio': settings.ANIO,
        'flimite': settings.FECHA_LIMITE,
        'fl_capcurs': settings.FL_CAPCURS,
        'fl_sinsevi': settings.FL_SINSEVI,
        'fl_siayb': settings.FL_SIAYB
    }
    template_name = 'panelde_control.html'
    #print(settings.TEMPLATES[0]['DIRS'])  # Imprime la ruta de búsqueda de las plantillas
    return render(request, template_name, {'config': config})

