from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


from routines.mkitsafe import valida_acceso
from routines.utils import requires_jquery_ui
from initsys.models import Usr

from .models import MedioActividad
from .forms import frmMedioActividad


@valida_acceso([
    'medioactividad.medios_de_actividad_app | medio actividad',
    'medioactividad.medios_de_actividad_medio actividad'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = list(MedioActividad.objects.all())
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'medioactividad.agregar_medio_de_actividad_app | medio actividad'
            ) or usuario.has_perm_or_has_perm_child(
                'medioactividad.agregar_medio_de_actividad_medio actividad'):
        toolbar.append({
            'type': 'link',
            'view': 'medioactividad_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    perms = {
        'see': usuario.has_perm_or_has_perm_child(
            'medioactividad.medios_de_actividad_app | medio actividad'
        ) or usuario.has_perm_or_has_perm_child(
            'medioactividad.medios_de_actividad_medio actividad'),
        'update': usuario.has_perm_or_has_perm_child(
            'medioactividad.actualizar_medio_de_actividad_app | medio actividad'
        ) or usuario.has_perm_or_has_perm_child(
            'medioactividad.actualizar_medio_de_actividad_medio actividad'),
        'delete': usuario.has_perm_or_has_perm_child(
            'medioactividad.eliminar_medio_de_actividad_app | medio actividad'
        ) or usuario.has_perm_or_has_perm_child(
            'medioactividad.eliminar_medio_de_actividad_medio actividad'),
    }
    return render(request, 'app/medioactividad/index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Medios de Actividad',
        'data': data,
        'toolbar': toolbar,
        'req_ui': requires_jquery_ui(request),
        'cperms': perms,
    })


@valida_acceso([
    'medioactividad.agregar_medio_de_actividad_app | medio actividad',
    'medioactividad.agregar_medio_de_actividad_medio actividad'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = frmMedioActividad(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.created_by = usuario
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('medioactividad_see', kwargs={
            'pk': obj.pk
        }))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Medio de Actividad',
        'titulo_descripcion': 'Nuevo',
        'frm': frm,
    })


@valida_acceso([
    'medioactividad.medios_de_actividad_app | medio actividad',
    'medioactividad.medios_de_actividad_medio actividad'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not MedioActividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = MedioActividad.objects.get(pk=pk)
    frm = frmMedioActividad(instance=obj)
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'medioactividad.medios_de_actividad_app | medio actividad'
            ) or usuario.has_perm_or_has_perm_child(
                'medioactividad.medios_de_actividad_medio actividad'):
        toolbar.append({
            'type': 'link',
            'view': 'medioactividad_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todos'})
    if usuario.has_perm_or_has_perm_child(
            'medioactividad.actualizar_medio_de_actividad_app | medio actividad'
            ) or usuario.has_perm_or_has_perm_child(
                'medioactividad.actualizar_medio_de_actividad_medio actividad'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'medioactividad_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child(
            'medioactividad.eliminar_medio_de_actividad_app | medio actividad'
            ) or usuario.has_perm_or_has_perm_child(
            'medioactividad.eliminar_medio_de_actividad_medio actividad'):
        toolbar.append({
            'type': 'link_pk_del',
            'view': 'medioactividad_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Medio de Actividad',
        'titulo_descripcion': obj,
        'frm': frm,
        'read_only': True,
        'toolbar': toolbar,
    })


@valida_acceso([
    'medioactividad.actualizar_medio_de_actividad_app | medio actividad',
    'medioactividad.actualizar_medio_de_actividad_medio actividad'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not MedioActividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = MedioActividad.objects.get(pk=pk)
    frm = frmMedioActividad(instance=obj, data=request.POST or None)
    if "POST" == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse(
            'medioactividad_see', kwargs={'pk': obj.pk}))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Medio de Actividad',
        'titulo_descripcion': obj,
        'frm': frm,
    })


@valida_acceso([
    'medioactividad.eliminar_medio_de_actividad_app | medio actividad',
    'medioactividad.eliminar_medio_de_actividad_medio actividad'])
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not MedioActividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = MedioActividad.objects.get(pk=pk)
    try:
        obj.delete()
        return HttpResponseRedirect(reverse('medioactividad_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))
