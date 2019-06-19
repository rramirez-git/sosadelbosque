from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from routines.mkitsafe import valida_acceso
from routines.utils import requires_jquery_ui
from initsys.models import Usr

from .models import UMA
from .forms import frmUMA

@valida_acceso(['uma.uma_uma'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = list(UMA.objects.all())
    toolbar = []
    if usuario.has_perm_or_has_perm_child('uma.agregar_uma_uma'):
        toolbar.append({
            'type': 'link',
            'view': 'uma_new',
            'label': '<i class="far fa-file"></i> Nueva'})
    perms = {
        'see': usuario.has_perm_or_has_perm_child('uma.uma_uma'),
        'update': usuario.has_perm_or_has_perm_child(
            'uma.actualizar_uma_uma'),
        'delete': usuario.has_perm_or_has_perm_child(
            'uma.eliminar_uma_uma'),
    }
    return render(request, 'app/uma/index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Unidades de Medida y Actualización (UMA)',
        'data': data,
        'toolbar': toolbar,
        'req_ui': requires_jquery_ui(request),
        'cperms': perms,
    })


@valida_acceso(['uma.agregar_uma_uma'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = frmUMA(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.created_by = usuario
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('uma_see', kwargs={
            'pk': obj.pk}))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Unidades de Medida y Actualización (UMA)',
        'titulo_descripcion': 'Nueva',
        'frm': frm,
    })


@valida_acceso(['uma.uma_uma'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not UMA.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = UMA.objects.get(pk=pk)
    frm = frmUMA(instance=obj)
    toolbar = []
    if usuario.has_perm_or_has_perm_child('uma.uma_uma'):
        toolbar.append({
            'type': 'link',
            'view': 'uma_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todas'})
    if usuario.has_perm_or_has_perm_child('uma.actualizar_uma_uma'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'uma_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child('uma.eliminar_uma_uma'):
        toolbar.append({
            'type': 'link_pk',
            'view':'uma_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Unidades de Medida y Actualización (UMA)',
        'titulo_descripcion': obj,
        'frm': frm,
        'read_only': True,
        'toolbar': toolbar,
    })


@valida_acceso(['uma.actualizar_uma_uma'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not UMA.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = UMA.objects.get(pk=pk)
    frm = frmUMA(instance=obj)
    print(request.method)
    print(frm.is_valid())
    print(frm.errors)
    if 'POST' == request.method and (frm.is_valid() or not frm.errors):
        obj = frm.save(commit=False)
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('uma_see', kwargs={
            'pk': obj.pk}))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Unidades de Medida y Actualización (UMA)',
        'titulo_descripcion': obj,
        'frm': frm,
    })


@valida_acceso(['uma.eliminar_uma_uma'])
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not UMA.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = UMA.objects.get(pk=pk)
    try:
        obj.delete()
        return HttpResponseRedirect(reverse('uma_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))