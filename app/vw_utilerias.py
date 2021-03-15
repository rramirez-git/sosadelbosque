from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.clickjacking import xframe_options_exempt

from routines.utils import requires_jquery_ui
from .models_historialaboral import *

def str2pesos(cantidad):
    return float(cantidad.replace('$', '').replace(',', ''))

@xframe_options_exempt
def simulador(request):
    data = {
        'anio_alta_imss_yr': int(request.POST.get("anio_alta_imss_yr", 1990)),
        'edad_qty': request.POST.get("edad_qty", 60),
        'semanas_amt': int(request.POST.get("semanas_amt", 500)),
        'concubino_flg': request.POST.get("concubino_flg", "no") == "yes",
        'hijos_qty': int(request.POST.get("hijos_qty", 0)),
        'anio_1': int(request.POST.get('anio_1', 1990)),
        'salario_1': str2pesos(request.POST.get('salario_1', "0")),
        'anio_2': int(request.POST.get('anio_2', 1990)),
        'salario_2': str2pesos(request.POST.get('salario_2', "0")),
        'anio_3': int(request.POST.get('anio_3', 1990)),
        'salario_3': str2pesos(request.POST.get('salario_3', "0")),
        'anio_4': int(request.POST.get('anio_4', 1990)),
        'salario_4': str2pesos(request.POST.get('salario_4', "0")),
        'anio_5': int(request.POST.get('anio_5', 1990)),
        'salario_5': str2pesos(request.POST.get('salario_5', "0")),
    }
    calculated = False
    results = {}
    if request.method == "POST":
        uma = UMA.objects.get(pk = getmaxUMA())
        salario_promedio_mensual = (
            data['salario_1'] + data['salario_2'] + data['salario_3'] \
                + data['salario_4'] + data['salario_5']) / 5
        uma_valor = uma.valor
        salario_promedio_diario = salario_promedio_mensual * 12 / 365
        aux_cbi = salario_promedio_diario / float(uma_valor)
        cbis = Cuantiabasica.objects.all()
        porcentaje_cuantia_basica = float(cbis[0].porcentaje_de_cuantia_basica)
        porcentaje_incremento_anual = float(cbis[0].porcentaje_de_incremento_anual)
        for elem in cbis:
            if elem.salario_inicio <= aux_cbi and aux_cbi <= elem.salario_fin:
                porcentaje_cuantia_basica = float(elem.porcentaje_de_cuantia_basica)
                porcentaje_incremento_anual = float(elem.porcentaje_de_incremento_anual)
        semanas = data['semanas_amt'] - 500
        semanas_restantes = semanas % 52
        anios_incremento = ((semanas - semanas_restantes) / 52)
        if semanas_restantes >= 27:
            anios_incremento += 1
        elif semanas_restantes >= 13:
            anios_incremento += 0.5
        porcentaje_cuantia_basica_incremento = porcentaje_cuantia_basica + anios_incremento * porcentaje_incremento_anual
        porcentaje_factor_actualizacion = 1.11
        porcentaje_factor_edad = float(Factoredad.objects.get(edad = data['edad_qty']).factor_de_edad)
        porcentaje_asignaciones_familiares = 0
        if data['concubino_flg']:
            porcentaje_asignaciones_familiares += 15
        if data['hijos_qty'] > 0:
            porcentaje_asignaciones_familiares += data['hijos_qty'] * 10
        pension = (porcentaje_cuantia_basica_incremento / 100) * (porcentaje_factor_edad / 100) * (porcentaje_factor_actualizacion) * ( 1 + porcentaje_asignaciones_familiares / 100) * salario_promedio_mensual
        porcentaje_pension = pension * 100 / salario_promedio_mensual
        results = {
            'semanas_cotizadas': data['semanas_amt'],
            'porcentaje_cuantia_basica': porcentaje_cuantia_basica,
            'porcentaje_incremento_anual': porcentaje_incremento_anual,
            'porcentaje_cuantia_basica_incremento': porcentaje_cuantia_basica_incremento,
            'pension': pension,
            'porcentaje_pension': porcentaje_pension,
            'salario_promedio_mensual': salario_promedio_mensual,
            'salario_promedio_diario': salario_promedio_diario,
            'porcentaje_factor_edad': porcentaje_factor_edad,
            'porcentaje_factor_actualizacion': porcentaje_factor_actualizacion,
            'porcentaje_asignaciones_familiares': porcentaje_asignaciones_familiares,
        }
        calculated = True
        print(f"porcentaje_cuantia_basica = {results['porcentaje_cuantia_basica']}")
        print(f"porcentaje_incremento_anual = {results['porcentaje_incremento_anual']}")
        print(f"porcentaje_cuantia_basica_incremento = {results['porcentaje_cuantia_basica_incremento']}")
        print(f"pension = {results['pension']}")
        print(f"porcentaje_pension = {results['porcentaje_pension']}")
        print(f"salario_promedio_mensual = {results['salario_promedio_mensual']}")
        print(f"salario_promedio_diario = {results['salario_promedio_diario']}")
        print(f"porcentaje_factor_edad = {results['porcentaje_factor_edad']}")
        print(f"porcentaje_factor_actualizacion = {results['porcentaje_factor_actualizacion']}")
        print(f"porcentaje_asignaciones_familiares = {results['porcentaje_asignaciones_familiares']}")
    return render(
        request,
        'app/utilerias/simulador.html', {
            'menu_main': {'perms': None}, 
            'titulo': "Simulador de Pension",
            'req_ui': requires_jquery_ui(request),
            'data': data,
            'results': results,
            'calculated': calculated,
        }
    )
