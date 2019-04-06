from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


from routines.mkitsafe import valida_acceso
from routines.utils import requires_jquery_ui
from initsys.models import Usr

from .models import TaxonomiaExpediente
from .forms import frmTaxonomia

@valida_acceso(['taxonomiaexpediente.taxonomia_taxonomia expediente'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = list(TaxonomiaExpediente.objects.all())
    toolbar = []
    if usuario.has_perm_or_has_perm_child('taxonomiaexpediente.agregar_taxonomia_taxonomia expediente'):
        toolbar.append({
            'type': 'link',
            'view': 'taxonomia_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    perms = {
        'see': usuario.has_perm_or_has_perm_child('taxonomiaexpediente.taxonomia_taxonomia expediente'),
        'update': usuario.has_perm_or_has_perm_child('taxonomiaexpediente.actualizar_taxonomia_taxonomia expediente'),
        'delete': usuario.has_perm_or_has_perm_child('taxonomiaexpediente.eliminar_taxonomia_taxonomia expediente'),
    }
    return render(request, 'app/taxonomiaexpediente/index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipos de Expediente',
        'data': data,
        'toolbar': toolbar,
        'req_ui': requires_jquery_ui(request),
        'cperms': perms,
    })


@valida_acceso(['taxonomiaexpediente.agregar_taxonomia_taxonomia expediente'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = frmTaxonomia(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.created_by = usuario
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('taxonomia_see', kwargs={
            'pk': obj.pk
        }))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipo de Expediente',
        'titulo_descripcion': 'Nuevo',
        'frm': frm,
    })


@valida_acceso(['taxonomiaexpediente.taxonomia_taxonomia expediente'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not TaxonomiaExpediente.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = TaxonomiaExpediente.objects.get(pk=pk)
    frm = frmTaxonomia(instance=obj)
    toolbar=[]
    if usuario.has_perm_or_has_perm_child('taxonomiaexpediente.taxonomia_taxonomia expediente'):
        toolbar.append({
            'type': 'link',
            'view': 'taxonomia_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todos'})
    if usuario.has_perm_or_has_perm_child('taxonomiaexpediente.actualizar_taxonomia_taxonomia expediente'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'taxonomia_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child('taxonomiaexpediente.eliminar_taxonomia_taxonomia expediente'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'taxonomia_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipo de Expediente',
        'titulo_descripcion': obj,
        'frm': frm,
        'read_only': True,
        'toolbar': toolbar,
    })


@valida_acceso()
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not TaxonomiaExpediente.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = TaxonomiaExpediente.objects.get(pk=pk)
    frm = frmTaxonomia(instance=obj, data=request.POST or None)
    if "POST" == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse(
            'taxonomia_see', kwargs={'pk': obj.pk}))
    return render(request,'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipo de Expediente',
        'titulo_descripcion': obj,
        'frm': frm,
    })

@valida_acceso(['taxonomiaexpediente.eliminar_taxonomia_taxonomia expediente'])
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not TaxonomiaExpediente.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = TaxonomiaExpediente.objects.get(pk=pk)
    try:
        obj.delete()
        return HttpResponseRedirect(reverse('taxonomia_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))
