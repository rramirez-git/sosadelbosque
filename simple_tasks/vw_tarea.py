from datetime import date
from calendar import monthrange

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import ProtectedError
from django.contrib.auth.models import User

from routines.mkitsafe import valida_acceso
from initsys.models import Usr
from app.models import (
    Cliente, HistoriaLaboral, Actividad, AssocCteTarea, AssocHistLabTarea,
    AssocActTarea)

from .functions import *
from .forms import FrmTarea
from .models import Tarea, STATUS_TAREA, Vinculo

@valida_acceso(['tarea.tareas_tarea'])
def index(request, anio=None, mes=None):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    toolbar = []
    if anio is None or anio < 2019:
        anio = date.today().year
        mes = date.today().month
    if mes is None or mes < 1 or mes > 12:
        mes = date.today().month
        anio = date.today().year
    next_month = NextMonthYear(anio, mes)
    prev_month = PrevMonthYear(anio, mes)
    if usuario.has_perm_or_has_perm_child('tarea.agregar_tareas_tarea'):
        toolbar.append({
            'type': 'button',
            'onclick': "openNewTaskFrm()",
            'label': '<i class="far fa-file"></i> Nueva Tarea'
        })
    toolbar.append({
        'type': 'rlink',
        'url': reverse('tarea_index', kwargs={
            'anio': prev_month['year'], 'mes':prev_month['month']}),
        'label': '<i class="fas fa-chevron-left"></i>'
    })
    toolbar.append({
        'type': 'rlink',
        'url': reverse('tarea_index', kwargs={
            'anio': next_month['year'], 'mes':next_month['month']}),
        'label': '<i class="fas fa-chevron-right"></i>'
    })
    cal = TaskCalendar()
    responsables = list(User.objects.exclude(id__in = Cliente.objects.all().values('id')))
    clientes = list(Cliente.objects.all())
    historias = list(HistoriaLaboral.objects.all())
    actividades = list(Actividad.objects.all())
    responsables.sort(key=lambda usr: f'{usr.first_name} {usr.last_name}'.upper())
    historias.sort(key=lambda obj: f'{obj}')
    actividades.sort(key=lambda obj: f'{obj.cliente} {obj}')
    return render(request, 'simple_tasks/index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tareas',
        'titulo_descripcion': f'{Num2Month(mes)} de {anio}',
        'toolbar': toolbar,
        'calendario': cal.formatmonth(anio, mes),
        'responsables': responsables,
        'status_tareas': STATUS_TAREA,
        'clientes': clientes,
        'historias_laborales': historias,
        'actividades': actividades,
        'anio': anio,
        'mes': mes,
    })

@valida_acceso(['tarea.agregar_tareas_tarea'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = {}
    if "POST" == request.method:
        frm = FrmTarea(request.POST or None)
        if frm.is_valid():
            obj = frm.save(commit=False)
            obj.created_by = usuario
            obj.updated_by = usuario
            obj.save()
            if request.POST.get('lnk_cte'):
                id = request.POST.get('lnk_cte')
                obj_vinc = Cliente.objects.get(pk=id)
                Vinculo.objects.create(
                    tarea=obj,
                    tipo="Cliente",
                    texto=f"{obj_vinc}",
                    url=reverse('cliente_see', kwargs={'pk': obj_vinc.pk}),
                    created_by=usuario,
                    updated_by=usuario
                )
                AssocCteTarea.objects.create(
                    cte=obj_vinc,
                    tarea=obj,
                    created_by=usuario,
                    updated_by=usuario
                )
            if request.POST.get('lnk_hl'):
                id = request.POST.get('lnk_hl')
                obj_vinc = HistoriaLaboral.objects.get(pk=id)
                Vinculo.objects.create(
                    tarea=obj,
                    tipo="Historia Laboral",
                    texto=f"{obj_vinc}",
                    url=reverse('cliente_historia_laboral', kwargs={'pk': obj_vinc.cliente.pk}),
                    created_by=usuario,
                    updated_by=usuario
                )
                AssocHistLabTarea.objects.create(
                    historial=obj_vinc,
                    tarea=obj,
                    created_by=usuario,
                    updated_by=usuario
                )
            if request.POST.get('lnk_act'):
                id = request.POST.get('lnk_act')
                obj_vinc = Actividad.objects.get(pk=id)
                Vinculo.objects.create(
                    tarea=obj,
                    tipo="Actividad",
                    texto=f"{obj_vinc.cliente} - {obj_vinc}",
                    url=reverse('actividad_see', kwargs={'pk': obj_vinc.pk}),
                    created_by=usuario,
                    updated_by=usuario
                )
                AssocActTarea.objects.create(
                    actividad=obj_vinc,
                    tarea=obj,
                    created_by=usuario,
                    updated_by=usuario
                )
            data = {'status': 'ok', 'id': obj.idtarea}
        else:
            data = {'status': 'error', 'id':1, 'reason': 'Wrong Data'}
    else:
        data = {'status': 'error', 'id':2, 'reason': 'Wrong Method'}
    return JsonResponse(data)

@valida_acceso(['tarea.tareas_tarea'])
def get_tasks(request, anio, mes):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    f_ini = date(anio, mes, 1)
    f_fin = date(anio, mes, monthrange(anio, mes)[1])
    if usuario.has_perm_or_has_perm_child(
            'tarea.tareas_de_todos_los_usuarios_tarea'):
        data = Tarea.objects.filter(
            fecha_limite__gte=f_ini, fecha_limite__lte=f_fin)
    else:
        data = Tarea.objects.filter(
            fecha_limite__gte=f_ini,
            fecha_limite__lte=f_fin,
            responsable=usuario)
    data = list(data.values(
        'idtarea',
        'titulo',
        'responsable',
        'fecha_limite',
        'estado_actual'))
    return JsonResponse(data, safe=False)
