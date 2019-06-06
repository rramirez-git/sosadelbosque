from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


from routines.mkitsafe import valida_acceso
from routines.utils import requires_jquery_ui
from initsys.models import Usr

from .models import TipoActividad
from .forms import frmTipoActividad

@valida_acceso(['tipoactividad.tipos_de_actividad_tipo actividad'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = list(TipoActividad.objects.all())
    toolbar = []
    if usuario.has_perm_or_has_perm_child('tipoactividad.agregar_tipo_de_actividad_tipo actividad'):
        toolbar.append({
            'type': 'link',
            'view': 'tipoactividad_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    perms = {
        'see': usuario.has_perm_or_has_perm_child('tipoactividad.tipos_de_actividad_tipo actividad'),
        'update': usuario.has_perm_or_has_perm_child('tipoactividad.actualizar_tipo_de_actividad_tipo actividad'),
        'delete': usuario.has_perm_or_has_perm_child('tipoactividad.eliminar_tipo_de_actividad_tipo actividad'),
    }
    return render(request, 'app/tipoactividad/index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipos de Actividad',
        'data': data,
        'toolbar': toolbar,
        'req_ui': requires_jquery_ui(request),
        'cperms': perms,
    })


@valida_acceso(['tipoactividad.agregar_tipo_de_actividad_tipo actividad'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = frmTipoActividad(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.created_by = usuario
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('tipoactividad_see', kwargs={
            'pk': obj.pk
        }))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipo de Actividad',
        'titulo_descripcion': 'Nuevo',
        'frm': frm,
    })


@valida_acceso(['tipoactividad.tipos_de_actividad_tipo actividad'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not TipoActividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = TipoActividad.objects.get(pk=pk)
    frm = frmTipoActividad(instance=obj)
    toolbar=[]
    if usuario.has_perm_or_has_perm_child('tipoactividad.tipos_de_actividad_tipo actividad'):
        toolbar.append({
            'type': 'link',
            'view': 'tipoactividad_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todos'})
    if usuario.has_perm_or_has_perm_child('tipoactividad.actualizar_tipo_de_actividad_tipo actividad'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'tipoactividad_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child('tipoactividad.eliminar_tipo_de_actividad_tipo actividad'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'tipoactividad_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipo de Actividad',
        'titulo_descripcion': obj,
        'frm': frm,
        'read_only': True,
        'toolbar': toolbar,
    })


@valida_acceso(['tipoactividad.actualizar_tipo_de_actividad_tipo actividad'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not TipoActividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = TipoActividad.objects.get(pk=pk)
    frm = frmTipoActividad(instance=obj, data=request.POST or None)
    if "POST" == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse(
            'tipoactividad_see', kwargs={'pk': obj.pk}))
    return render(request,'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipo de Actividad',
        'titulo_descripcion': obj,
        'frm': frm,
    })

@valida_acceso(['tipoactividad.eliminar_tipo_de_actividad_tipo actividad'])
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not TipoActividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = TipoActividad.objects.get(pk=pk)
    try:
        obj.delete()
        return HttpResponseRedirect(reverse('tipoactividad_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))
