from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


from routines.mkitsafe import valida_acceso
from routines.utils import requires_jquery_ui
from initsys.models import Usr

from .models import Actividad, Cliente
from .forms import frmActividad, frmActividadUpd, frmActividadHistoria

@valida_acceso()
def index(request):
    return ""
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
        'titulo': 'Actividad',
        'data': data,
        'toolbar': toolbar,
        'req_ui': requires_jquery_ui(request),
        'cperms': perms,
    })


@valida_acceso()
def new(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    cliente = Cliente.objects.get(pk=pk)
    frm = frmActividad(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.created_by = usuario
        obj.updated_by = usuario
        obj.cliente = cliente
        obj.save()
        return HttpResponseRedirect(reverse('actividad_see', kwargs={
            'pk': obj.pk
        }))
    return render(request, 'app/actividad/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Actividad',
        'titulo_descripcion': 'Nueva - {}'.format(cliente),
        'frm': frm,
    })


@valida_acceso()
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Actividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Actividad.objects.get(pk=pk)
    if 'POST' == request.method:
        if 'add-history' == request.POST.get('action'):
            frmActHist = frmActividadHistoria(request.POST)
            if frmActHist.is_valid():
                actHist = frmActHist.save(commit=False)
                actHist.created_by = usuario
                actHist.updated_by = usuario
                actHist.estado_anterior = obj.estado
                actHist.actividad = obj
                actHist.save()
                obj.estado = actHist.estado_nuevo
                obj.save()
    frm = frmActividad(instance=obj)
    toolbar=[]
    toolbar.append({
        'type': 'link_pk',
        'view': 'cliente_see',
        'label': '<i class="far fa-eye"></i> Ver Cliente',
        'pk': obj.cliente.pk})
    toolbar.append({
        'type': 'button',
        'onclick': 'ActividadHistoria.showFrmNew()',
        'label': '<i class="fas fa-map-marker-alt"></i> Actualizar Estado'})
    toolbar.append({
        'type': 'link_pk',
        'view': 'actividad_update',
        'label': '<i class="far fa-edit"></i> Actualizar',
        'pk': pk})
    toolbar.append({
        'type': 'link_pk',
        'view': 'actividad_delete',
        'label': '<i class="far fa-trash-alt"></i> Eliminar',
        'pk': pk})
    return render(request, 'app/actividad/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Actividad',
        'titulo_descripcion': "{} - {}".format( obj, obj.cliente),
        'frm': frm,
        'read_only': True,
        'toolbar': toolbar,
        'frmActHist': frmActividadHistoria(),
        'act': obj,
    })


@valida_acceso()
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Actividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Actividad.objects.get(pk=pk)
    frm = frmActividadUpd(instance=obj, data=request.POST or None)
    if "POST" == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.updated_by = usuario
        obj.save()
        return HttpResponseRedirect(reverse(
            'actividad_see', kwargs={'pk': obj.pk}))
    return render(request,'app/actividad/form.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Actividad',
        'titulo_descripcion': "{} - {}".format( obj, obj.cliente),
        'frm': frm,
    })

@valida_acceso()
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Actividad.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Actividad.objects.get(pk=pk)
    cte_pk = obj.cliente.pk
    try:
        obj.delete()
        return HttpResponseRedirect(reverse('cliente_see', kwargs={'pk': cte_pk}))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))
