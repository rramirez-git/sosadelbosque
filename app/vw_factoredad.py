from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from routines.mkitsafe import valida_acceso
from routines.utils import requires_jquery_ui
from initsys.models import Usr

from .models import Factoredad
from .forms import frmFactorEdad


@valida_acceso(['factoredad.factoredad_factoredad'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = list(Factoredad.objects.all())
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'factoredad.agregar_factoredad_factoredad'):
        toolbar.append({
            'type': 'link',
            'view': 'factoredad_new',
            'label': '<i class="far fa-file"></i> Nueva'})
    perms = {
        'see': usuario.has_perm_or_has_perm_child(
            'factoredad.factoredad_factoredad'),
        'update': usuario.has_perm_or_has_perm_child(
            'factoredad.actualizar_factoredad_factoredad'),
        'delete': usuario.has_perm_or_has_perm_child(
            'factoredad.eliminar_factoredad_factoredad'),
    }
    return render(request, 'app/factoredad/index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Factor de Edad',
        'data': data,
        'toolbar': toolbar,
        'req_ui': requires_jquery_ui(request),
        'cperms': perms,
    })


@valida_acceso(['factoredad.agregar_factoredad_factoredad'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = frmFactorEdad(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.created_by = usuario
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('factoredad_see', kwargs={
            'pk': obj.pk}))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Factor de Edad',
        'titulo_descripcion': 'Nuevo',
        'frm': frm,
    })


@valida_acceso(['factoredad.factoredad_factoredad'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Factoredad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Factoredad.objects.get(pk=pk)
    frm = frmFactorEdad(instance=obj)
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'factoredad.factoredad_factoredad'):
        toolbar.append({
            'type': 'link',
            'view': 'factoredad_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todas'})
    if usuario.has_perm_or_has_perm_child(
            'factoredad.actualizar_factoredad_factoredad'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'factoredad_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child(
            'factoredad.eliminar_factoredad_factoredad'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'factoredad_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Factor de Edad',
        'titulo_descripcion': obj,
        'frm': frm,
        'read_only': True,
        'toolbar': toolbar,
    })


@valida_acceso(['factoredad.actualizar_factoredad_factoredad'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Factoredad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Factoredad.objects.get(pk=pk)
    frm = frmFactorEdad(instance=obj, data=request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('factoredad_see', kwargs={
            'pk': obj.pk}))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Factor de Edad',
        'titulo_descripcion': obj,
        'frm': frm,
    })


@valida_acceso(['factoredad.eliminar_factoredad_factoredad'])
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Factoredad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Factoredad.objects.get(pk=pk)
    try:
        obj.delete()
        return HttpResponseRedirect(reverse('factoredad_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))
