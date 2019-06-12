from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


from routines.mkitsafe import valida_acceso
from routines.utils import requires_jquery_ui
from initsys.models import Usr

from .models import Externo
from .forms import frmExterno


@valida_acceso(['externo.externos_externo'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = list(Externo.objects.all())
    toolbar = []
    if usuario.has_perm_or_has_perm_child('externo.agregar_externo_externo'):
        toolbar.append({
            'type': 'link',
            'view': 'externo_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    perms = {
        'see': usuario.has_perm_or_has_perm_child(
            'externo.externos_externo'),
        'update': usuario.has_perm_or_has_perm_child(
            'externo.actualizar_externo_externo'),
        'delete': usuario.has_perm_or_has_perm_child(
            'externo.eliminar_externo_externo'),
    }
    return render(request, 'app/externo/index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Personas Externas',
        'data': data,
        'toolbar': toolbar,
        'req_ui': requires_jquery_ui(request),
        'cperms': perms,
    })


@valida_acceso(['externo.agregar_externo_externo'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = frmExterno(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.created_by = usuario
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('externo_see', kwargs={
            'pk': obj.pk
        }))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Persona Externa',
        'titulo_descripcion': 'Nuevo',
        'frm': frm,
    })


@valida_acceso(['externo.externos_externo'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Externo.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Externo.objects.get(pk=pk)
    frm = frmExterno(instance=obj)
    toolbar = []
    if usuario.has_perm_or_has_perm_child('externo.externos_externo'):
        toolbar.append({
            'type': 'link',
            'view': 'externo_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todos'})
    if usuario.has_perm_or_has_perm_child(
            'externo.actualizar_externo_externo'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'externo_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child(
            'externo.eliminar_externo_externo'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'externo_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Persona Externa',
        'titulo_descripcion': obj,
        'frm': frm,
        'read_only': True,
        'toolbar': toolbar,
    })


@valida_acceso(['externo.actualizar_externo_externo'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Externo.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Externo.objects.get(pk=pk)
    frm = frmExterno(instance=obj, data=request.POST or None)
    if "POST" == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse(
            'externo_see', kwargs={'pk': obj.pk}))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Persona Externa',
        'titulo_descripcion': obj,
        'frm': frm,
    })


@valida_acceso(['externo.eliminar_externo_externo'])
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Externo.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Externo.objects.get(pk=pk)
    try:
        obj.delete()
        return HttpResponseRedirect(reverse('externo_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))
