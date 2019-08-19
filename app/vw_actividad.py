from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


from routines.mkitsafe import valida_acceso
from routines.utils import requires_jquery_ui
from initsys.models import Usr

from .models import (
    Actividad, Cliente, TipoActividad, EstatusActividad, Externo)
from .forms import frmActividad, frmActividadUpd, frmActividadHistoria


@valida_acceso()
def index(request):
    return ""
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = list(TipoActividad.objects.all())
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'tipoactividad.agregar_tipo_de_actividad_tipo actividad'):
        toolbar.append({
            'type': 'link',
            'view': 'tipoactividad_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    perms = {
        'see': usuario.has_perm_or_has_perm_child(
            'tipoactividad.tipos_de_actividad_tipo actividad'),
        'update': usuario.has_perm_or_has_perm_child(
            'tipoactividad.actualizar_tipo_de_actividad_tipo actividad'),
        'delete': usuario.has_perm_or_has_perm_child(
            'tipoactividad.eliminar_tipo_de_actividad_tipo actividad'),
    }
    return render(request, 'app/tipoactividad/index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Actividad',
        'data': data,
        'toolbar': toolbar,
        'req_ui': requires_jquery_ui(request),
        'cperms': perms,
    })


@valida_acceso(['actividad.agregar_actividad_actividad'])
def new(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    cliente = Cliente.objects.get(pk=pk)
    frm = frmActividad(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.created_by = usuario
        obj.updated_by = usuario
        obj.cliente = cliente
        obj.save()
        return HttpResponseRedirect(reverse('actividad_see', kwargs={
            'pk': obj.pk
        }))
    return render(request, 'app/actividad/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Actividad',
        'titulo_descripcion': 'Nueva - {}'.format(cliente),
        'frm': frm,
    })


@valida_acceso(['actividad.actividad_actividad'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Actividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Actividad.objects.get(pk=pk)
    if 'POST' == request.method:
        if 'add-history' == request.POST.get('action'):
            frmActHist = frmActividadHistoria(request.POST)
            if frmActHist.is_valid():
                actHist = frmActHist.save(commit=False)
                actHist.created_by = usuario
                actHist.updated_by = usuario
                actHist.estado_anterior = obj.estado
                actHist.actividad = obj
                actHist.save()
                obj.estado = actHist.estado_nuevo
                obj.save()
    frm = frmActividad(instance=obj)
    toolbar = []
    if usuario.has_perm_or_has_perm_child('cliente.clientes_cliente'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'cliente_see',
            'label': '<i class="far fa-eye"></i> Ver Cliente',
            'pk': obj.cliente.pk})
    if usuario.has_perm_or_has_perm_child(
            'actividad.actualizar_estado_actividad'):
        toolbar.append({
            'type': 'button',
            'onclick': 'ActividadHistoria.showFrmNew()',
            'label':
                '<i class="fas fa-map-marker-alt"></i> Actualizar Estado'})
    if usuario.has_perm_or_has_perm_child(
            'actividad.actualizar_actividad_actividad'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'actividad_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child(
            'actividad.eliminar_actividad_actividad'):
        toolbar.append({
            'type': 'link_pk_del',
            'view': 'actividad_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'app/actividad/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Actividad',
        'titulo_descripcion': "{} - {}".format(obj, obj.cliente),
        'frm': frm,
        'read_only': True,
        'toolbar': toolbar,
        'frmActHist': frmActividadHistoria(),
        'act': obj,
    })


@valida_acceso(['actividad.actualizar_actividad_actividad'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Actividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Actividad.objects.get(pk=pk)
    frm = frmActividadUpd(instance=obj, data=request.POST or None)
    if "POST" == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse(
            'actividad_see', kwargs={'pk': obj.pk}))
    return render(request, 'app/actividad/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Actividad',
        'titulo_descripcion': "{} - {}".format(obj, obj.cliente),
        'frm': frm,
    })


@valida_acceso(['actividad.eliminar_actividad_actividad'])
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Actividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Actividad.objects.get(pk=pk)
    cte_pk = obj.cliente.pk
    try:
        obj.delete()
        return HttpResponseRedirect(
            reverse('cliente_see', kwargs={'pk': cte_pk}))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))


@valida_acceso([
    'permission.maestro_de_actividades_permiso',
    'permission.maestro_de_actividades_permission'])
def reporte_maestro(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = []
    ftr_tipo_actividad = int(
        "0" + request.POST.get('ftr_tipo_actividad', ''))
    ftr_estatus_actividad = int(
        "0" + request.POST.get('ftr_estatus_actividad', ''))
    ftr_responsable = int("0" + request.POST.get('ftr_responsable', ''))
    if "POST" == request.method:
        data = Actividad.objects.all()
        if ftr_tipo_actividad:
            data = data.filter(tipo_de_actividad__pk=ftr_tipo_actividad)
        if ftr_estatus_actividad:
            data = data.filter(estado__pk=ftr_estatus_actividad)
        if ftr_responsable:
            data = data.filter(responsable__pk=ftr_responsable)
        data = list(data)
    return render(request, 'app/actividad/reporte_maestro.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Actividad',
        'titulo_descripcion': "Reporte Maestro",
        'req_ui': requires_jquery_ui(request),
        'combo_options': {
            'tipo_actividad': list(TipoActividad.objects.all()),
            'estatus_actividad': list(EstatusActividad.objects.all()),
            'responsable': list(Externo.objects.all()),
        },
        'filters': {
            'ftr_tipo_actividad': ftr_tipo_actividad,
            'ftr_estatus_actividad': ftr_estatus_actividad,
            'ftr_responsable': ftr_responsable,
        },
        'regs': data,
    })
