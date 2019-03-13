from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Permission
from django.db.models import ProtectedError

from .forms import FrmPermiso
from .models import Permiso, Usr
from routines.mkitsafe import valida_acceso
from routines.utils import clean_name, hipernormalize


@valida_acceso(['permiso.permisos_permiso'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    search_value = ""
    root_perms = Permiso.objects.filter(permiso_padre__isnull=True)
    data = []
    for obj in root_perms:
        aux = PermisoTableStruct(obj)
        for p in aux:
            data.append(p)
    if "POST" == request.method:
        if "search" == request.POST.get('action'):
            search_value = hipernormalize(request.POST.get('valor'))
            data = [reg
                    for reg in data if (
                        search_value in hipernormalize(reg.nombre)
                        or search_value in hipernormalize(reg.mostrar_como)
                        or search_value in hipernormalize(reg.descripcion)
                        or search_value in hipernormalize(reg.vista)
                        or search_value in hipernormalize(reg.permiso_padre)
                        or search_value in hipernormalize(reg.name)
                        or search_value in hipernormalize(reg.content_type)
                        or search_value in hipernormalize(reg.codename))
                    ]
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'permiso.agregar_permisos_permiso'):
        toolbar.append({
            'type': 'link',
            'view': 'permiso_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    if usuario.has_perm_or_has_perm_child('permission.perms_permission'):
        toolbar.append({
            'type': 'link',
            'view': 'permission_index',
            'label': '<i class="fas fa-glasses"></i> Perms'})
    toolbar.append({'type': 'search'})
    return render(
        request,
        'initsys/permiso/index.html', {
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Permisos',
            'data': data,
            'toolbar': toolbar,
            'search_value': search_value,
            })


@valida_acceso(['permiso.agregar_permisos_permiso'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = FrmPermiso(request.POST or None)
    if frm.is_valid():
        obj = frm.save(commit=False)
        obj.name = obj.nombre
        obj.created_by = usuario
        obj.codename = "{}_{}".format(
            clean_name(obj.nombre), obj.content_type)
        obj.save()
        return HttpResponseRedirect(reverse(
            'permiso_see', kwargs={'pk': obj.pk}))
    return render(
        request,
        'global/form.html', {
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Permisos',
            'titulo_descripcion': 'Nuevo',
            'frm': frm
            })


@valida_acceso(['permiso.permisos_permiso'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Permiso.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse(
            'item_no_encontrado'))
    obj = Permiso.objects.get(pk=pk)
    frm = FrmPermiso(instance=obj)
    toolbar = []
    if usuario.has_perm_or_has_perm_child('permiso.permisos_permiso'):
        toolbar.append({
            'type': 'link',
            'view': 'permiso_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todos'})
    if usuario.has_perm_or_has_perm_child(
            'permiso.actualizar_permisos_permiso'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'permiso_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child(
            'permiso.eliminar_permisos_permiso'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'permiso_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(
        request,
        'initsys/permiso/see.html', {
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Permisos',
            'titulo_descripcion': obj,
            'read_only': True,
            'frm': frm,
            'toolbar': toolbar,
            'arbol': PermisoStruct(obj)
            })


@valida_acceso(['permiso.actualizar_permisos_permiso'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Permiso.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse(
            'item_no_encontrado'))
    obj = Permiso.objects.get(pk=pk)
    if "POST" == request.method:
        frm = FrmPermiso(instance=obj, data=request.POST)
        if frm.is_valid():
            obj = frm.save(commit=False)
            obj.name = obj.nombre
            obj.codename = "{}_{}".format(
                clean_name(obj.nombre), obj.content_type)
            obj.updated_by = usuario
            obj.save()
            return HttpResponseRedirect(reverse(
                'permiso_see', kwargs={'pk': obj.pk}))
        else:
            return render(
                request,
                'global/form.html', {
                    'menu_main': usuario.main_menu_struct(),
                    'titulo': 'Permisos',
                    'titulo_descripcion': obj,
                    'frm': frm
                    })
    else:
        frm = FrmPermiso(instance=obj)
        return render(
            request,
            'global/form.html', {
                'menu_main': usuario.main_menu_struct(),
                'titulo': 'Permisos',
                'titulo_descripcion': obj,
                'frm': frm
                })


@valida_acceso(['permiso.eliminar_permisos_permiso'])
def delete(request, pk):
    try:
        if not Permiso.objects.filter(pk=pk).exists():
            return HttpResponseRedirect(reverse(
                'item_no_encontrado'))
        obj = Permiso.objects.get(pk=pk)
        obj.delete()
        return HttpResponseRedirect(reverse('permiso_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse(
            'item_con_relaciones'))


@valida_acceso(['permission.perms_permission'])
def permission_index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    search_value = ""
    data = Permission.objects.all().order_by('content_type')
    if "POST" == request.method:
        if "search" == request.POST.get('action'):
            search_value = hipernormalize(request.POST.get('valor'))
            data = [reg
                    for reg in data if (
                        search_value in hipernormalize(reg.name)
                        or search_value in hipernormalize(reg.content_type)
                        or search_value in hipernormalize(reg.codename))
                    ]
    toolbar = []
    if usuario.has_perm_or_has_perm_child('permiso.permisos_permiso'):
        toolbar.append({
            'type': 'link',
            'view': 'permiso_index',
            'label': '<i class="fas fa-glasses"></i> Permisos'
        })
    toolbar.append({'type': 'search'})
    return render(request, 'initsys/permiso/permission.html', {
        'data': data,
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Permission',
        'toolbar': toolbar,
        'search_value': search_value,
    })


def PermisoStruct(permiso, level=0):
    linea = '{}{}<br />'.format("&nbsp;" * (level * 4), permiso)
    for p in permiso.hijos():
        linea += PermisoStruct(p, level + 1)
    return linea


def PermisoTableStruct(permiso):
    hijos = [permiso]
    aux = Permiso.objects.filter(permiso_padre__pk=permiso.pk)
    for p in aux:
        aux2 = PermisoTableStruct(p)
        for p2 in aux2:
            hijos.append(p2)
    return hijos
