from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from routines.mkitsafe import valida_acceso
from routines.utils import requires_jquery_ui
from initsys.models import Usr

from .models import Cuantiabasica
from .forms import frmCuantiaBasica


@valida_acceso(['cuantiabasica.cuantiabasica_cuantiabasica'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = list(Cuantiabasica.objects.all())
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'cuantiabasica.agregar_cuantiabasica_cuantiabasica'):
        toolbar.append({
            'type': 'link',
            'view': 'cuantiabasica_new',
            'label': '<i class="far fa-file"></i> Nueva'})
    perms = {
        'see': usuario.has_perm_or_has_perm_child(
            'cuantiabasica.cuantiabasica_cuantiabasica'),
        'update': usuario.has_perm_or_has_perm_child(
            'cuantiabasica.actualizar_cuantiabasica_cuantiabasica'),
        'delete': usuario.has_perm_or_has_perm_child(
            'cuantiabasica.eliminar_cuantiabasica_cuantiabasica'),
    }
    return render(request, 'app/cuantiabasica/index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Cuantía Básica e Incremento Anual',
        'data': data,
        'toolbar': toolbar,
        'req_ui': requires_jquery_ui(request),
        'cperms': perms,
    })


@valida_acceso(['cuantiabasica.agregar_cuantiabasica_cuantiabasica'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = frmCuantiaBasica(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.created_by = usuario
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('cuantiabasica_see', kwargs={
            'pk': obj.pk}))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Cuantía Básica e Incremento Anual',
        'titulo_descripcion': 'Nueva',
        'frm': frm,
    })


@valida_acceso(['cuantiabasica.cuantiabasica_cuantiabasica'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Cuantiabasica.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Cuantiabasica.objects.get(pk=pk)
    frm = frmCuantiaBasica(instance=obj)
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'cuantiabasica.cuantiabasica_cuantiabasica'):
        toolbar.append({
            'type': 'link',
            'view': 'cuantiabasica_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todas'})
    if usuario.has_perm_or_has_perm_child(
            'cuantiabasica.actualizar_cuantiabasica_cuantiabasica'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'cuantiabasica_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child(
            'cuantiabasica.eliminar_cuantiabasica_cuantiabasica'):
        toolbar.append({
            'type': 'link_pk_del',
            'view': 'cuantiabasica_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Cuantía Básica e Incremento Anual',
        'titulo_descripcion': obj,
        'frm': frm,
        'read_only': True,
        'toolbar': toolbar,
    })


@valida_acceso(['cuantiabasica.actualizar_cuantiabasica_cuantiabasica'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Cuantiabasica.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Cuantiabasica.objects.get(pk=pk)
    frm = frmCuantiaBasica(instance=obj, data=request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('cuantiabasica_see', kwargs={
            'pk': obj.pk}))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Cuantía Básica e Incremento Anual',
        'titulo_descripcion': obj,
        'frm': frm,
    })


@valida_acceso(['cuantiabasica.eliminar_cuantiabasica_cuantiabasica'])
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Cuantiabasica.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Cuantiabasica.objects.get(pk=pk)
    try:
        obj.delete()
        return HttpResponseRedirect(reverse('cuantiabasica_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))
