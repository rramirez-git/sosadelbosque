from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

from routines.mkitsafe import valida_acceso

from initsys.models import Usr
from .models import Cliente, HistoriaLaboralRegistro
from app.data_utils import df_load_HLRD_periodo_continuo_laborado

@valida_acceso(['permission.mis_documentos_permiso', 'permission.mis_documentos_permission'])
def mis_documentos(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    cte = None
    if Cliente.objects.filter(idusuario=usuario.pk).exists():
        cte = Cliente.objects.get(idusuario=usuario.pk)
    return render(
        request,
        'app/me_as_cte/mis_documentos.html',{
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Mis Documentos',
            'cte': cte,
        })

@valida_acceso(['permission.mi_salario_promedio_permiso', 'permission.mi_salario_promedio_permission'])
def mi_salario_promedio(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    cte = None
    if Cliente.objects.filter(idusuario=usuario.pk).exists():
        cte = Cliente.objects.get(idusuario=usuario.pk)
    return render(
        request,
        'app/me_as_cte/mi_salario_promedio.html',{
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Mi Salario Promedio',
            'cte': cte,
        })

@valida_acceso(['permission.mi_historial_laboral_permiso', 'permission.mi_historial_laboral_permission'])
def mi_historial_laboral(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    cte = None
    df_pers = None
    aggr_per_lab = None
    if Cliente.objects.filter(idusuario=usuario.pk).exists():
        cte = Cliente.objects.get(idusuario=usuario.pk)
        df_pers = df_load_HLRD_periodo_continuo_laborado(cte.pk)
        df_pers[
            'historialaboralregistro'
            ] = df_pers.historialaboralregistro_pk.apply(
                lambda x: HistoriaLaboralRegistro.objects.get(pk=x).__str__()
                )
        df_pers_agg = df_pers.agg(['min', 'max', 'sum'])
        f_max = df_pers_agg.fecha_fin['max']
        f_min = df_pers_agg.fecha_inicio['min']
        dias_t = (f_max - f_min).days + 1
        aggr_per_lab = {
            'dias_transc': dias_t,
            'dias_rec': df_pers_agg.dias_cotiz['sum'],
            'sem_rec': df_pers_agg.semanas_cotiz['sum'],
            'anios_rec': df_pers_agg.anios_cotiz['sum'],
            'dias_inac': df_pers_agg.dias_inact['sum'],
            'sem_inac': df_pers_agg.semanas_inact['sum'],
            'anios_inac': df_pers_agg.anios_inact['sum'],
            'sem_transc': round(dias_t / 7),
            'anios_transc': round(dias_t / 7) / 52,
        }
        aggr_per_lab['dias_dif'] = aggr_per_lab['dias_transc'] - aggr_per_lab['dias_rec'] - aggr_per_lab['dias_inac']
        aggr_per_lab['sem_dif'] = round(aggr_per_lab['dias_dif'] / 7)
        aggr_per_lab['anios_dif'] = round(aggr_per_lab['dias_dif'] / 7) / 52
    return render(
        request,
        'app/me_as_cte/mi_historial_laboral.html',{
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Mi Historial Laboral',
            'cte': cte,
            'aggr_per_lab': aggr_per_lab,
            'peridodos_laborados': df_pers,
        })

@valida_acceso(['permission.mis_opciones_de_pension_permiso', 'permission.mis_opciones_de_pension_permission'])
def mis_opciones_pension(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    cte = None
    if Cliente.objects.filter(idusuario=usuario.pk).exists():
        cte = Cliente.objects.get(idusuario=usuario.pk)
    return render(
        request,
        'app/me_as_cte/mis_opciones_pension.html',{
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Mis Opciones de Pensión',
            'cte': cte,
        })