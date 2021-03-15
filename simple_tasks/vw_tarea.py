from datetime import date
from calendar import monthrange
import json

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import ProtectedError
from django.contrib.auth.models import User

from routines.mkitsafe import valida_acceso
from routines.utils import (
    as_paragraph_fn, hipernormalize, requires_jquery_ui)
from initsys.models import Usr
from app.models import (
    Cliente, HistoriaLaboral, Actividad, AssocCteTarea, AssocHistLabTarea,
    AssocActTarea)

from .functions import *
from .forms import FrmTarea
from .models import Tarea, STATUS_TAREA, Vinculo, Comentario, Historia


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
            'anio': prev_month['year'], 'mes': prev_month['month']}),
        'label': '<i class="fas fa-chevron-left"></i>'
    })
    toolbar.append({
        'type': 'rlink',
        'url': reverse('tarea_index', kwargs={
            'anio': next_month['year'], 'mes': next_month['month']}),
        'label': '<i class="fas fa-chevron-right"></i>'
    })
    cal = TaskCalendar()
    responsables = list(User.objects.exclude(
        id__in=Cliente.objects.all().values('id')))
    clientes = list(Cliente.objects.all())
    historias = list(HistoriaLaboral.objects.all())
    actividades = list(Actividad.objects.all())
    responsables.sort(
        key=lambda usr: f'{usr.first_name} {usr.last_name}'.upper())
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
                crearlink(id, "Cliente", obj, usuario)
            if request.POST.get('lnk_hl'):
                id = request.POST.get('lnk_hl')
                crearlink(id, "Historia Laboral", obj, usuario)
            if request.POST.get('lnk_act'):
                id = request.POST.get('lnk_act')
                crearlink(id, "Actividad", obj, usuario)
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
    data2 = []
    for item in data:
        try:
            data2.append({
                'idtarea': item.idtarea,
                'titulo': item.titulo,
                'responsable': item.responsable.pk,
                'fecha_limite': item.fecha_limite,
                'estado_actual': item.estado_actual,
                'color': item.color})
        except AttributeError as e:
            data2.append({
                'idtarea': item.idtarea,
                'titulo': item.titulo,
                'responsable': 10,
                'fecha_limite': item.fecha_limite,
                'estado_actual': item.estado_actual,
                'color': item.color})
    return JsonResponse(data2, safe=False)


@valida_acceso(['tarea.tareas_tarea'])
def get_task(request, pk=0):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    obj = Tarea.objects.get(pk = pk)
    if obj.responsable is None:
        obj.responsable = User.objects.get(pk=10)
    if obj.created_by is None:
        obj.created_by = User.objects.get(pk=10)
    if obj.updated_by is None:
        obj.updated_by = User.objects.get(pk=10)
    data = {
        'pk': pk,
        'titulo': obj.titulo,
        'descripcion': as_paragraph_fn(obj.descripcion),
        'descripcion_raw': obj.descripcion,
        'responsable': {
            'pk': obj.responsable.pk,
            'first_name': obj.responsable.first_name,
            'last_name': obj.responsable.last_name
        },
        'fecha_limite': obj.fecha_limite.strftime("%d/%m/%Y"),
        'fecha_limite_en': obj.fecha_limite.strftime("%Y-%m-%d"),
        'estado_actual': obj.estado_actual,
        'vinculos': [{
            'pk': lnk.pk,
            'tipo': lnk.tipo,
            'url': lnk.url,
            'texto': lnk.texto} for lnk in obj.vinclulos.all()],
        'historia': [
            {
                'cambio': 'Fecha de Creación',
                'valor_anterior': None,
                'valor_nuevo': None,
                'at': obj.created_at.strftime("%d/%m/%Y %H:%M"),
                'by': f"{obj.created_by.first_name} {obj.created_by.last_name}"
            },
            {
                'cambio': 'Fecha de Actualizacion',
                'valor_anterior': None,
                'valor_nuevo': None,
                'at':obj.updated_at.strftime("%d/%m/%Y %H:%M"),
                'by': f"{obj.updated_by.first_name} {obj.updated_by.last_name}"
            }
        ] + [{
            'cambio': hist.cambio,
            'valor_anterior': hist.valor_anterior,
            'valor_nuevo': hist.valor_nuevo,
            'at': hist.created_at.strftime("%d/%m/%Y %H:%M"),
            'by': f"{hist.created_by.first_name} {hist.created_by.last_name}"
        } for hist in obj.historia.all()],
        'comentarios': [{
            'pk': comentario.pk,
            'comentario': as_paragraph_fn(comentario.comentario),
            'comentario_raw': comentario.comentario,
            'at': comentario.updated_at.strftime("%d/%m/%Y %H:%M"),
            'by':
                f"{comentario.created_by.first_name} {comentario.created_by.last_name}",
            'editable': (usuario.has_perm_or_has_perm_child(
                    'comentario.actualizar_comentarios_comentario'
                ) and comentario.created_by.id == usuario.id),
            'eliminable': (usuario.has_perm_or_has_perm_child(
                    'comentario.eliminar_comentarios_comentario'
                ) and comentario.created_by.id == usuario.id),
            } for comentario in obj.comentarios.all()]
    }
    return JsonResponse(data, safe=False)


@valida_acceso(['tarea.tareas_tarea'])
def add_coment(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = {}
    if "POST" == request.method:
        id = request.POST.get('id')
        comentario = request.POST.get('comentario')
        if id and comentario:
            obj = Comentario.objects.create(
                tarea=Tarea.objects.get(pk=id),
                comentario=comentario,
                created_by=usuario,
                updated_by=usuario
            )
            data = {'status': 'ok', 'id': obj.pk}
        else:
            data = {'status': 'error', 'id':1, 'reason': 'Wrong Data'}
    else:
        data = {'status': 'error', 'id':2, 'reason': 'Wrong Method'}
    return JsonResponse(data)


@valida_acceso(['tarea.eliminar_tareas_tarea'])
def delete_tarea(request, pk=0):
    Tarea.objects.get(pk=pk).delete()
    data = {'status': 'ok', 'id': 'deleted'}
    return JsonResponse(data)


@valida_acceso(['comentario.eliminar_comentarios_comentario'])
def delete_comentario(request, pk=0):
    Comentario.objects.get(pk=pk).delete()
    data = {'status': 'ok', 'id': 'deleted'}
    return JsonResponse(data)


@valida_acceso(['tarea.actualizar_tareas_tarea'])
def update(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = {}
    if "POST" == request.method:
        pk = request.POST.get('pk')
        if not Tarea.objects.filter(pk=pk).exists():
            data = {'status': 'error', 'id':4, 'reason': 'Object doesn\'t exists'}
        else:
            obj = Tarea.objects.get(pk=pk)
            obj_base = Tarea.objects.get(pk=pk)
            frm = FrmTarea(instance=obj, data=request.POST or None)
            if frm.is_valid():
                obj = frm.save(commit=False)
                obj.updated_by = usuario
                obj.save()
                if obj.titulo != obj_base.titulo:
                    Historia.objects.create(
                        tarea=obj,
                        cambio="Tarea",
                        valor_anterior=obj_base.titulo,
                        valor_nuevo=obj.titulo,
                        created_by=usuario)
                if obj.descripcion != obj_base.descripcion:
                    Historia.objects.create(
                        tarea=obj,
                        cambio="Descripción",
                        valor_anterior=obj_base.descripcion,
                        valor_nuevo=obj.descripcion,
                        created_by=usuario)
                if obj.responsable.pk != obj_base.responsable.pk:
                    Historia.objects.create(
                        tarea=obj,
                        cambio="Responsable",
                        valor_anterior=f"{obj_base.responsable}",
                        valor_nuevo=f"{obj.responsable}",
                        created_by=usuario)
                if obj.fecha_limite != obj_base.fecha_limite:
                    Historia.objects.create(
                        tarea=obj,
                        cambio="Fecha Límite",
                        valor_anterior=obj_base.fecha_limite.strftime("%d/%m/%Y"),
                        valor_nuevo=obj.fecha_limite.strftime("%d/%m/%Y"),
                        created_by=usuario)
                if obj.estado_actual != obj_base.estado_actual:
                    Historia.objects.create(
                        tarea=obj,
                        cambio="Estado Actual",
                        valor_anterior=obj_base.estado_actual,
                        valor_nuevo=obj.estado_actual,
                        created_by=usuario)
                data = {'status': 'ok', 'id': obj.pk}
            else:
                data = {'status': 'error', 'id':1, 'reason': 'Wrong Data'}
    else:
        data = {'status': 'error', 'id':2, 'reason': 'Wrong Method'}
    return JsonResponse(data)


@valida_acceso(['comentario.actualizar_comentarios_comentario'])
def update_comentario(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = {}
    if "POST" == request.method:
        pk = request.POST.get('pk')
        comentario = request.POST.get('comentario')
        obj = Comentario.objects.get(pk=pk)
        obj.comentario = comentario
        obj.updated_by = usuario
        obj.save()
        data = {'status': 'ok', 'id': obj.pk}
    else:
        data = {'status': 'error', 'id':2, 'reason': 'Wrong Method'}
    return JsonResponse(data)


@valida_acceso(['tarea.actualizar_tareas_tarea'])
def delete_link(request):
    pk = request.POST.get("pk")
    obj = Vinculo.objects.get(pk=pk)
    if obj.tipo == "Cliente":
        AssocCteTarea.objects.get(tarea=obj.tarea).delete()
    if obj.tipo == "Historia Laboral":
        AssocHistLabTarea.objects.get(tarea=obj.tarea).delete()
    if obj.tipo == "Actividad":
        AssocActTarea.objects.get(tarea=obj.tarea).delete()
    obj.delete()
    data = {'status': 'ok'}
    return JsonResponse(data)


@valida_acceso(['tarea.actualizar_tareas_tarea'])
def new_link(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    id = request.POST.get("id")
    tipo = request.POST.get("tipo")
    idtarea = request.POST.get("idtarea")
    tarea = Tarea.objects.get(pk=request.POST.get("idtarea"))
    crearlink(
        request.POST.get("id"),
        request.POST.get("tipo"),
        Tarea.objects.get(pk=request.POST.get("idtarea")),
        Usr.objects.filter(id=request.user.pk)[0]
        )
    data = {'status': 'ok'}
    return JsonResponse(data)


@valida_acceso([
    'permission.maestro_de_tareas_permiso',
    'permission.maestro_de_tareas_permiso'])
def reporte_maestro(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = []
    anio = date.today().year
    mes = date.today().month
    ftr = {
        'ftr_fecha_limite_inicio': request.POST.get(
            'ftr_fecha_limite_inicio', date(
                anio, mes, 1).strftime("%Y-%m-%d")),
        'ftr_fecha_limite_fin': request.POST.get(
            'ftr_fecha_limite_fin', date(anio, mes, monthrange(
                anio, mes)[1]).strftime("%Y-%m-%d")),
        'ftr_usuario_responsable': hipernormalize(request.POST.get(
            'ftr_usuario_responsable', '')),
        'ftr_estado_actual': hipernormalize(request.POST.get(
            'ftr_estado_actual', '')),
    }
    print(ftr)
    if "POST" == request.method:
        if ftr['ftr_fecha_limite_inicio'] == '':
            ftr['ftr_fecha_limite_inicio'] = date(
                anio, mes, 1).strftime("%Y-%m-%d")
        if ftr['ftr_fecha_limite_fin'] == '':
            ftr['ftr_fecha_limite_fin'] = date(
                anio, mes, monthrange(anio, mes)[1]).strftime("%Y-%m-%d")
        data = Tarea.objects.filter(
            fecha_limite__gte=ftr['ftr_fecha_limite_inicio'],
            fecha_limite__lte=ftr['ftr_fecha_limite_fin'])
        if ftr['ftr_usuario_responsable']:
            data = [
                elem for elem in data
                if ("{} {}".format(
                    hipernormalize(elem.responsable.first_name),
                    hipernormalize(elem.responsable.last_name)
                )).find(ftr['ftr_usuario_responsable']) >= 0
            ]
        if ftr['ftr_estado_actual']:
            data = [
                elem for elem in data
                if hipernormalize(elem.estado_actual).find(
                    ftr['ftr_estado_actual']) >= 0
            ]
    responsables = list(User.objects.exclude(id__in = Cliente.objects.all().values('id')))
    clientes = list(Cliente.objects.all())
    historias = list(HistoriaLaboral.objects.all())
    actividades = list(Actividad.objects.all())
    responsables.sort(key=lambda usr: f'{usr.first_name} {usr.last_name}'.upper())
    historias.sort(key=lambda obj: f'{obj}')
    actividades.sort(key=lambda obj: f'{obj.cliente} {obj}')
    return render(request, 'simple_tasks/reporte_maestro.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tareas',
        'titulo_descripcion': "Reporte Maestro",
        'req_ui': requires_jquery_ui(request),
        'filters': ftr,
        'regs': data,
        'responsables': responsables,
        'status_tareas': STATUS_TAREA,
        'clientes': clientes,
        'historias_laborales': historias,
        'actividades': actividades,
    })


def crearlink(id, tipo, tarea, usuario):
    if "Cliente" == tipo:
        obj_vinc = Cliente.objects.get(pk=id)
        url = reverse('cliente_see', kwargs={'pk': obj_vinc.pk})
        assoc = AssocCteTarea
        assoc.objects.create(
            cte=obj_vinc,
            tarea=tarea,
            created_by=usuario,
            updated_by=usuario
        )
        txt = f"{obj_vinc}"
    elif "Historia Laboral" == tipo:
        obj_vinc = HistoriaLaboral.objects.get(pk=id)
        url = reverse('cliente_historia_laboral', kwargs={'pk': obj_vinc.cliente.pk})
        assoc = AssocHistLabTarea
        assoc.objects.create(
            historial=obj_vinc,
            tarea=tarea,
            created_by=usuario,
            updated_by=usuario
        )
        txt = f"{obj_vinc}"
    elif "Actividad" == tipo:
        obj_vinc = Actividad.objects.get(pk=id)
        url = reverse('actividad_see', kwargs={'pk': obj_vinc.pk})
        assoc = AssocActTarea
        assoc.objects.create(
            actividad=obj_vinc,
            tarea=tarea,
            created_by=usuario,
            updated_by=usuario
        )
        txt = f"{obj_vinc.cliente} - {obj_vinc}"
    Vinculo.objects.create(
        tarea=tarea,
        tipo=tipo,
        texto=txt,
        url=url,
        created_by=usuario,
        updated_by=usuario
    )
