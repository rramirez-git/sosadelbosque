from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


from routines.mkitsafe import valida_acceso
from routines.utils import requires_jquery_ui
from initsys.models import Usr

from .models import TipoDocumento
from .forms import frmTipoDocumento

@valida_acceso(['tipodocumento.tipos_de_documento_tipo documento'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = list(TipoDocumento.objects.all())
    toolbar = []
    if usuario.has_perm_or_has_perm_child('tipodocumento.agregar_tipo_de_documento_tipo documento'):
        toolbar.append({
            'type': 'link',
            'view': 'tipodocumento_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    perms = {
        'see': usuario.has_perm_or_has_perm_child('tipodocumento.tipos_de_documento_tipo documento'),
        'update': usuario.has_perm_or_has_perm_child('tipodocumento.actualizar_tipo_de_documento_tipo documento'),
        'delete': usuario.has_perm_or_has_perm_child('tipodocumento.eliminar_tipo_de_documento_tipo documento'),
    }
    return render(request, 'app/tipodocumento/index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipos de Documento',
        'data': data,
        'toolbar': toolbar,
        'req_ui': requires_jquery_ui(request),
        'cperms': perms,
    })


@valida_acceso(['tipodocumento.agregar_tipo_de_documento_tipo documento'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = frmTipoDocumento(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.created_by = usuario
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse('tipodocumento_see', kwargs={
            'pk': obj.pk
        }))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipo de Documento',
        'titulo_descripcion': 'Nuevo',
        'frm': frm,
    })


@valida_acceso(['tipodocumento.tipos_de_documento_tipo documento'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not TipoDocumento.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = TipoDocumento.objects.get(pk=pk)
    frm = frmTipoDocumento(instance=obj)
    toolbar=[]
    if usuario.has_perm_or_has_perm_child('tipodocumento.tipos_de_documento_tipo documento'):
        toolbar.append({
            'type': 'link',
            'view': 'tipodocumento_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todos'})
    if usuario.has_perm_or_has_perm_child('tipodocumento.actualizar_tipo_de_documento_tipo documento'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'tipodocumento_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child('tipodocumento.eliminar_tipo_de_documento_tipo documento'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'tipodocumento_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipo de Documento',
        'titulo_descripcion': obj,
        'frm': frm,
        'read_only': True,
        'toolbar': toolbar,
    })


@valida_acceso(['tipodocumento.actualizar_tipo_de_documento_tipo documento'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not TipoDocumento.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = TipoDocumento.objects.get(pk=pk)
    frm = frmTipoDocumento(instance=obj, data=request.POST or None)
    if "POST" == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse(
            'tipodocumento_see', kwargs={'pk': obj.pk}))
    return render(request,'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Tipo de Documento',
        'titulo_descripcion': obj,
        'frm': frm,
    })

@valida_acceso(['tipodocumento.eliminar_tipo_de_documento_tipo documento'])
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not TipoDocumento.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = TipoDocumento.objects.get(pk=pk)
    try:
        obj.delete()
        return HttpResponseRedirect(reverse('tipodocumento_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))
