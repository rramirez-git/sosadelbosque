from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

from .forms import FrmSetting
from .models import Setting, Usr, setting_upload_to
from routines.utils import move_uploaded_file, hipernormalize
from routines.mkitsafe import valida_acceso


@valida_acceso()
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    search_value = ""
    data = Setting.objects.filter(es_multiple=False)
    if "POST" == request.method:
        if "singles" == request.POST.get('action'):
            parametros = Setting.objects.filter(es_multiple=False)
            for parametro in parametros:
                if("INTEGER" == parametro.tipo
                        or "STRING" == parametro.tipo
                        or "TEXT" == parametro.tipo):
                    valor = request.POST.get(parametro.nombre)
                    if valor is not None:
                        parametro.valor = valor
                        parametro.save()
                elif ("PICTURE" == parametro.tipo
                        or "FILE" == parametro.tipo):
                    file = request.FILES.get(parametro.nombre)
                    if file is not None:
                        parametro.valor = move_uploaded_file(
                            file, setting_upload_to)
                        parametro.save()
            data = Setting.objects.filter(es_multiple=False)
        elif "search" == request.POST.get('action'):
            search_value = hipernormalize(request.POST.get('valor'))
            data = [reg
                    for reg in data if (
                        search_value in hipernormalize(reg.seccion)
                        or search_value in hipernormalize(reg.nombre)
                        or search_value in hipernormalize(
                            reg.nombre_para_mostrar)
                        or search_value in hipernormalize(reg.tipo))
                    ]
    toolbar = []
    toolbar.append({'type': 'search'})
    return render(
        request,
        'initsys/setting/values.html', {
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Parámetros del Sistema',
            'singles': data,
            'multiples': Setting.objects.filter(es_multiple=True),
            'toolbar': toolbar,
            'search_value': search_value,
        })


@valida_acceso(['setting.administrar_settings_setting'])
def index_adm(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    search_value = ""
    data = Setting.objects.all()
    if "POST" == request.method:
        if "search" == request.POST.get('action'):
            search_value = hipernormalize(request.POST.get('valor'))
            data = [reg
                    for reg in data if (
                        search_value in hipernormalize(reg.seccion)
                        or search_value in hipernormalize(reg.nombre)
                        or search_value in hipernormalize(
                            reg.nombre_para_mostrar)
                        or search_value in hipernormalize(reg.tipo))
                    ]
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'setting.agregar_settings_setting'):
        toolbar.append({
            'type': 'link',
            'view': 'setting_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    toolbar.append({'type': 'search'})
    return render(
        request,
        'initsys/setting/index.html', {
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Administración de Parámetros',
            'data': data,
            'toolbar': toolbar,
            'search_value': search_value,
        })


@valida_acceso(['setting.agregar_settings_setting'])
def new_adm(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = FrmSetting(request.POST or None)
    if 'POST' == request.method:
        if frm.is_valid():
            obj = frm.save()
            return HttpResponseRedirect(reverse(
                'setting_see', kwargs={'pk': obj.pk}))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Parámetro',
        'titulo_descripcion': 'Nuevo',
        'frm': frm
    })


@valida_acceso(['setting.agregar_settings_setting'])
def see_adm(request, pk):
    if not Setting.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse(
            'item_no_encontrado'))
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    obj = Setting.objects.get(pk=pk)
    frm = FrmSetting(instance=obj)
    toolbar = []
    if usuario.has_perm_or_has_perm_child(
            'setting.administrar_settings_setting'):
        toolbar.append({
            'type': 'link',
            'view': 'setting_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todos'})
    if usuario.has_perm_or_has_perm_child(
            'setting.actualizar_settings_setting'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'setting_update',
            'label': '<i class="far fa-edit"></i> Actualizar', 'pk': pk})
    if usuario.has_perm_or_has_perm_child(
            'setting.eliminar_settings_setting'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'setting_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Parámetro',
        'titulo_descripcion': obj,
        'read_only': True,
        'frm': frm,
        'toolbar': toolbar
    })


@valida_acceso(['setting.actualizar_settings_setting'])
def update_adm(request, pk):
    if not Setting.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse(
            'item_no_encontrado'))
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    obj = Setting.objects.get(pk=pk)
    frm = FrmSetting(instance=obj, data=request.POST or None)
    if 'POST' == request.method:
        if frm.is_valid():
            obj = frm.save()
            return HttpResponseRedirect(reverse(
                'setting_see', kwargs={'pk': obj.pk}))
    return render(request, 'global/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Parámetro',
        'titulo_descripcion': obj,
        'frm': frm
    })


@valida_acceso(['setting.eliminar_settings_setting'])
def delete_adm(request, pk):
    if not Setting.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse(
            'item_no_encontrado'))
    Setting.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse('setting_index'))
