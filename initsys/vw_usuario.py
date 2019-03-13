from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.conf import settings
from random import randint
from os.path import isfile
from os import remove

from .forms import FrmUsuario
from .models import Usr, usr_upload_to
from routines.mkitsafe import valida_acceso
from routines.utils import move_uploaded_file, hipernormalize


@valida_acceso(['usr.usuarios_usuario', 'usr.usuarios_user'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    root_usrs = Usr.objects.filter(depende_de__isnull=True)
    search_value = ""
    data = []
    for obj in root_usrs:
        data.append(obj)
        for h in obj.descendencia():
            data.append(h)
    if "POST" == request.method:
        if "search" == request.POST.get('action'):
            search_value = hipernormalize(request.POST.get('valor'))
            data = [reg
                    for reg in data if (
                        search_value in hipernormalize(reg.usuario)
                        or search_value in hipernormalize(reg.email)
                        or search_value in hipernormalize(reg.telefono)
                        or search_value in hipernormalize(reg.celular)
                        or search_value in hipernormalize(reg.first_name)
                        or search_value in hipernormalize(reg.last_name))
                    ]
    toolbar = []
    if usuario.has_perm_or_has_perm_child('usr.agregar_usuarios_usuario') or usuario.has_perm_or_has_perm_child('usr.agregar_usuarios_user'):
        toolbar.append({
            'type': 'link',
            'view': 'usuario_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    if usuario.has_perm_or_has_perm_child('user.users_usuario') or usuario.has_perm_or_has_perm_child('user.users_user'):
        toolbar.append({
            'type': 'link',
            'view': 'user_index',
            'label': '<i class="fas fa-glasses"></i> Users'})
    toolbar.append({'type': 'search'})
    return render(
        request,
        'initsys/usuario/index.html', {
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Usuarios',
            'data': data,
            'toolbar': toolbar,
            'search_value': search_value,
            })


@valida_acceso(['usr.agregar_usuarios_usuario', 'usr.agregar_usuarios_user'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if 'POST' == request.method:
        frm = FrmUsuario(request.POST)
        if frm.is_valid():
            obj = frm.save(commit=False)
            obj.username = obj.usuario
            obj.set_password(obj.contraseña)
            obj.created_by = usuario
            if request.FILES.get('fotografia'):
                obj.fotografia = move_uploaded_file(
                    request.FILES.get('fotografia'), usr_upload_to)
            obj.save()
            obj.groups.set(request.POST.getlist('groups'))
            obj.save()
            return HttpResponseRedirect(reverse(
                'usuario_see', kwargs={'pk': obj.pk}))
    frm = FrmUsuario(request.POST or None)
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Usuarios',
        'titulo_descripcion': 'Nuevo',
        'frm': frm
        })


@valida_acceso(['usr.usuarios_usuario', 'usr.usuarios_user'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Usr.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse(
            'item_no_encontrado'))
    obj = Usr.objects.get(pk=pk)
    frm = FrmUsuario(instance=obj)
    arbol = [obj]
    for u in obj.descendencia():
        arbol.append(u)
    toolbar = []
    if usuario.has_perm_or_has_perm_child('usr.usuarios_usuario') or usuario.has_perm_or_has_perm_child('usr.usuarios_user'):
        toolbar.append({
            'type': 'link',
            'view': 'usuario_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todos'})
    if usuario.has_perm_or_has_perm_child('usr.actualizar_usuarios_usuario') or usuario.has_perm_or_has_perm_child('usr.actualizar_usuarios_user'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'usuario_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child('usr.eliminar_usuarios_usuario') or usuario.has_perm_or_has_perm_child('usr.eliminar_usuarios_user'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'usuario_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'initsys/usuario/see.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Usuarios',
        'titulo_descripcion': obj,
        'read_only': True,
        'frm': frm,
        'fotografia': obj.fotografia,
        'toolbar': toolbar,
        'arbol': arbol
        })


@valida_acceso(['usr.actualizar_usuarios_usuario', 'usr.actualizar_usuarios_user'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Usr.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse(
            'item_no_encontrado'))
    usr = Usr.objects.get(pk=pk)
    if 'POST' == request.method:
        frm = FrmUsuario(instance=usr, data=request.POST)
        if frm.is_valid():
            obj = frm.save(commit=False)
            obj.username = obj.usuario
            obj.set_password(obj.contraseña)
            obj.updated_by = usuario
            if request.FILES.get('fotografia'):
                obj.fotografia = move_uploaded_file(
                    request.FILES.get('fotografia'), usr_upload_to)
            obj.save()
            obj.groups.clear()
            obj.groups.set(request.POST.getlist('groups'))
            obj.save()
            return HttpResponseRedirect(reverse(
                'usuario_see', kwargs={'pk': obj.pk}))
        else:
            return render(request, 'global/form.html', {
                'menu_main': usuario.main_menu_struct(),
                'titulo': 'Usuarios',
                'titulo_descripcion': usr,
                'frm': frm
                })
    else:
        frm = FrmUsuario(instance=usr)
        return render(request, 'global/form.html', {
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Usuarios',
            'titulo_descripcion': usr,
            'frm': frm
            })


@valida_acceso(['usr.eliminar_usuarios_usuario', 'usr.eliminar_usuarios_user'])
def delete(request, pk):
    try:
        if not Usr.objects.filter(pk=pk).exists():
            return HttpResponseRedirect(reverse(
                'item_no_encontrado'))
        Usr.objects.get(pk=pk).delete()
        return HttpResponseRedirect(reverse('usuario_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse(
            'item_con_relaciones'))


@valida_acceso(['user.users_usuario', 'user.users_user'])
def user_index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    search_value = ""
    data = User.objects.all()
    if "POST" == request.method:
        if "search" == request.POST.get('action'):
            search_value = hipernormalize(request.POST.get('valor'))
            data = [reg
                    for reg in data if (
                        search_value in hipernormalize(reg.username)
                        or search_value in hipernormalize(reg.email)
                        or search_value in hipernormalize(reg.first_name)
                        or search_value in hipernormalize(reg.last_name))
                    ]
    toolbar = []
    if usuario.has_perm_or_has_perm_child('usr.usuarios_usuario') or usuario.has_perm_or_has_perm_child('usr.usuarios_user'):
        toolbar.append({
            'type': 'link',
            'view': 'usuario_index',
            'label': '<i class="fas fa-glasses"></i> Usuarios'})
    toolbar.append({'type': 'search'})
    return render(
        request,
        'initsys/users/index.html',
        {
            'data': data,
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Root Users',
            'toolbar': toolbar,
            'search_value': search_value,
        }
    )
