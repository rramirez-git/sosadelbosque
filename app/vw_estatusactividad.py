from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


from routines.mkitsafe import valida_acceso
from routines.utils import requires_jquery_ui
from initsys.models import Usr

from .models import EstatusActividad
from .forms import frmEstatusActividad


@valida_acceso(['estatusactividad.estatus_de_actividad_estatus actividad'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = list(EstatusActividad.objects.all())
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'estatusactividad.agregar_estatus_de_actividad_estatus actividad'):
        toolbar.append({
            'type': 'link',
            'view': 'estatusactividad_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    perms = {
        'see': usuario.has_perm_or_has_perm_child(
            'estatusactividad.estatus_de_actividad_estatus actividad'),
        'update': usuario.has_perm_or_has_perm_child(
            'estatusactividad.'
            'actualizar_estatus_de_actividad_estatus actividad'
            ),
        'delete': usuario.has_perm_or_has_perm_child(
            'estatusactividad.eliminar_estatus_de_actividad_estatus actividad'
            ),
    }
    return render(request, 'app/estatusactividad/index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Estatus de Actividad',
        'data': data,
        'toolbar': toolbar,
        'req_ui': requires_jquery_ui(request),
        'cperms': perms,
    })


@valida_acceso([
    'estatusactividad.agregar_estatus_de_actividad_estatus actividad'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = frmEstatusActividad(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.created_by = usuario
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('estatusactividad_see', kwargs={
            'pk': obj.pk
        }))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Estatus de Actividad',
        'titulo_descripcion': 'Nuevo',
        'frm': frm,
    })


@valida_acceso(['estatusactividad.estatus_de_actividad_estatus actividad'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not EstatusActividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = EstatusActividad.objects.get(pk=pk)
    frm = frmEstatusActividad(instance=obj)
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'estatusactividad.estatus_de_actividad_estatus actividad'):
        toolbar.append({
            'type': 'link',
            'view': 'estatusactividad_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todos'})
    if usuario.has_perm_or_has_perm_child(
            'estatusactividad.'
            'actualizar_estatus_de_actividad_estatus actividad'
            ):
        toolbar.append({
            'type': 'link_pk',
            'view': 'estatusactividad_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child(
            'estatusactividad.eliminar_estatus_de_actividad_estatus actividad'
            ):
        toolbar.append({
            'type': 'link_pk_del',
            'view': 'estatusactividad_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Estatus de Actividad',
        'titulo_descripcion': obj,
        'frm': frm,
        'read_only': True,
        'toolbar': toolbar,
    })


@valida_acceso([
    'estatusactividad.actualizar_estatus_de_actividad_estatus actividad'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not EstatusActividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = EstatusActividad.objects.get(pk=pk)
    frm = frmEstatusActividad(instance=obj, data=request.POST or None)
    if "POST" == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse(
            'estatusactividad_see', kwargs={'pk': obj.pk}))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Estatus de Actividad',
        'titulo_descripcion': obj,
        'frm': frm,
    })


@valida_acceso([
    'estatusactividad.eliminar_estatus_de_actividad_estatus actividad'])
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not EstatusActividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = EstatusActividad.objects.get(pk=pk)
    try:
        obj.delete()
        return HttpResponseRedirect(reverse('estatusactividad_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))
