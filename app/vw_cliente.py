from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.db.models import ProtectedError

from routines.mkitsafe import valida_acceso

from .models import Cliente, TaxonomiaExpediente, HistoriaLaboral
from .forms import (
    frmCliente, frmClienteContacto, frmClienteUsuario, frmDocument,
    frmClienteObservaciones)
from initsys.forms import FrmDireccion
from initsys.models import Usr, Nota, Alerta, usr_upload_to
from routines.utils import requires_jquery_ui, move_uploaded_file


def add_nota(cte, nota, fecha_notificacion, usr):
    if "" != nota.strip():
        nota = Nota.objects.create(
            usuario=cte,
            nota=nota,
            created_by=usr,
            updated_by=usr,
        )
        if "" != fecha_notificacion:
            add_alert(
                "En referencia al cliente {}:\n\n{}".format(cte, nota),
                fecha_notificacion,
                usr,
                usr)


def add_alert(nota, fecha_notificacion, usr_to, usr_creator):
    if "" != nota.strip() and "" != fecha_notificacion:
        Alerta.objects.create(
            usuario=usr_to,
            nota=nota,
            fecha_alerta=fecha_notificacion,
            created_by=usr_creator,
            updated_by=usr_creator
        )


@valida_acceso(['cliente.clientes_cliente'])
def index(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = list(Cliente.objects.all())
    toolbar = []
    if usuario.has_perm_or_has_perm_child('cliente.agregar_clientes_cliente'):
        toolbar.append({
            'type': 'link',
            'view': 'cliente_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    return render(
        request,
        'app/cliente/index.html', {
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Clientes',
            'data': data,
            'toolbar': toolbar,
            'req_ui': requires_jquery_ui(request),
            })


@valida_acceso(['cliente.agregar_clientes_cliente'])
def new(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    frm = frmCliente(request.POST or None)
    frmCteCont = frmClienteContacto(request.POST or None)
    frmCteUsr = frmClienteUsuario(request.POST or None)
    frmCteDir = FrmDireccion(request.POST or None)
    frmCteObs = frmClienteObservaciones(request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.username = obj.usuario
        obj.set_password(obj.contraseña)
        obj.created_by = usuario
        obj.updated_by = usuario
        direccion = frmCteDir.save()
        obj.domicilicio = direccion
        if request.FILES.get('fotografia'):
            obj.fotografia = move_uploaded_file(
                request.FILES.get('fotografia'), usr_upload_to)
        obj.save()
        obj.groups.add(Group.objects.get(name='Cliente'))
        obj.save()
        return HttpResponseRedirect(reverse(
            'cliente_see', kwargs={'pk': obj.pk}
        ))
    return render(request, 'global/form2.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Clientes',
        'titulo_descripcion': 'Nuevo',
        'req_ui': requires_jquery_ui(request),
        'titulo_frm_1': 'Datos Generales',
        'frm': frmCteUsr,
        'titulo_frm_4': "Contacto",
        'frm4': frmCteCont,
        'titulo_frm_5': 'Dirección',
        'frm5': frmCteDir,
        'frm7': frmCteObs,
    })


@valida_acceso(['cliente.clientes_cliente'])
def see(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Cliente.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Cliente.objects.get(pk=pk)
    frmCteCont = frmClienteContacto(instance=obj)
    frmCteUsr = frmClienteUsuario(instance=obj)
    frmCteDir = FrmDireccion(instance=obj.domicilicio)
    frmCteObs = frmClienteObservaciones(instance=obj)
    if 'POST' == request.method:
        if "add-note" == request.POST.get('action'):
            add_nota(
                obj,
                request.POST.get('nota').strip(),
                request.POST.get('fecha_notificacion'),
                usuario)
        elif "add-alert" == request.POST.get("action"):
            add_alert(
                request.POST.get('nota').strip(),
                request.POST.get('fecha_notificacion'),
                obj,
                usuario
            )
        elif "add-document":
            frmDocto = frmDocument(request.POST or None, request.FILES)
            docto = frmDocto.save(commit=False)
            docto.cliente = obj
            docto.created_by = usuario
            docto.updated_by = usuario
            docto.save()
    toolbar = []
    if usuario.has_perm_or_has_perm_child('cliente.clientes_cliente'):
        toolbar.append({
            'type': 'link',
            'view': 'cliente_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todos'})
    toolbar.append({
        'type': 'button',
        'label': '<i class="far fa-comment-alt"></i> Notas',
        'onclick': 'Cte.showNotasSglCte()',
    })
    toolbar.append({
        'type': 'button',
        'label': '<i class="far fa-bell"></i> Alerta',
        'onclick': 'Cte.showAlertsSglCte()',
    })
    toolbar.append({
        'type': 'button',
        'label': '<i class="fas fa-file-upload"></i> Adjuntar',
        'onclick': 'Cte.showFrmDoctoGral()'
    })
    toolbar.append({
        'type': 'link_pk',
        'view': 'actividad_new',
        'label': '<i class="fas fa-paperclip"></i> Actividad',
        'pk': obj.pk
    })
    if usuario.has_perm_or_has_perm_child(
            'cliente.actualizar_clientes_cliente'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'cliente_update',
            'label': '<i class="far fa-edit"></i> Actualizar',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child(
            'cliente.eliminar_clientes_cliente'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'cliente_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    return render(request, 'app/cliente/see.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Clientes',
        'titulo_descripcion': obj,
        'req_ui': requires_jquery_ui(request),
        'read_only': True,
        'toolbar': toolbar,
        'titulo_frm_1': 'Datos Generales',
        'frm': frmCteUsr,
        'titulo_frm_4': "Contacto",
        'frm4': frmCteCont,
        'titulo_frm_5': 'Dirección',
        'frm5': frmCteDir,
        'cte': obj,
        'frmDocto': frmDocument(),
        'frmObs': frmCteObs,
    })


@valida_acceso(['cliente.actualizar_clientes_cliente'])
def update(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Cliente.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Cliente.objects.get(pk=pk)
    frm = frmCliente(instance=obj, data=request.POST or None)
    frmCteCont = frmClienteContacto(
        instance=obj, data=request.POST or None)
    frmCteUsr = frmClienteUsuario(
        instance=obj, data=request.POST or None)
    frmCteDir = FrmDireccion(
        instance=obj.domicilicio, data=request.POST or None)
    frmCteObs = frmClienteObservaciones(
        instance=obj, data=request.POST or None)
    if 'POST' == request.method and frm.is_valid():
        obj = frm.save(commit=False)
        obj.username = obj.usuario
        obj.set_password(obj.contraseña)
        obj.updated_by = usuario
        if request.FILES.get('fotografia'):
            obj.fotografia = move_uploaded_file(
                request.FILES.get('fotografia'), usr_upload_to)
        obj.save()
        obj.groups.add(Group.objects.get(name='Cliente'))
        obj.save()
        return HttpResponseRedirect(reverse(
            'cliente_see', kwargs={'pk': obj.pk}
        ))
    return render(request, 'global/form2.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Clientes',
        'titulo_descripcion': obj,
        'req_ui': requires_jquery_ui(request),
        'titulo_frm_1': 'Datos Generales',
        'frm': frmCteUsr,
        'titulo_frm_4': "Contacto",
        'frm4': frmCteCont,
        'titulo_frm_5': 'Dirección',
        'frm5': frmCteDir,
        'frm7': frmCteObs,
    })


@valida_acceso(['cliente.eliminar_clientes_cliente'])
def delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Cliente.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = Cliente.objects.get(pk=pk)
    try:
        obj.delete()
        return HttpResponseRedirect(reverse('cliente_index'))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))


@valida_acceso([
    'permission.maestro_de_clientes_permiso',
    'permission.maestro_de_clientes_permission'])
def reporte_maestro(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    data = []
    ftr_tipo_expediente = int(
        "0" + request.POST.get('ftr_tipo_expediente', ''))
    ftr_edad_inicio = int("0" + request.POST.get('ftr_edad_inicio', ''))
    ftr_edad_fin = int("0" + request.POST.get('ftr_edad_fin', ''))
    if "POST" == request.method:
        data = Cliente.objects.all()
        if ftr_tipo_expediente:
            data = data.filter(tipo__pk=ftr_tipo_expediente)
        data = list(data)
        if ftr_edad_inicio:
            data = [elem for elem in data if ftr_edad_inicio <= elem.edad]
        if ftr_edad_fin:
            data = [elem for elem in data if elem.edad <= ftr_edad_fin]
    return render(request, 'app/cliente/reporte_maestro.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Clientes',
        'titulo_descripcion': "Reporte Maestro",
        'req_ui': requires_jquery_ui(request),
        'combo_options': {
            'tipo_expediente': list(TaxonomiaExpediente.objects.all()),
        },
        'filters': {
            'ftr_tipo_expediente': ftr_tipo_expediente,
            'ftr_edad_inicio': ftr_edad_inicio,
            'ftr_edad_fin': ftr_edad_fin,
        },
        'regs': data,
    })


@valida_acceso(['cliente.clientes_cliente'])
def historia_laboral(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    cte = Cliente.objects.get(pk=pk)
    if HistoriaLaboral.objects.filter(cliente=cte).exists():
        historia = HistoriaLaboral.objects.get(cliente=cte)
    else:
        historia = HistoriaLaboral.objects.create(
            cliente=cte, created_by=usuario, updated_by=usuario)
        historia.save()
    toolbar = []
    toolbar.append({
        'type': 'link_pk',
        'view': 'cliente_see',
        'label': '<i class="far fa-eye"></i> Ver Cliente',
        'pk': cte.pk})
    toolbar.append({
        'type': 'button',
        'label': '<i class="far fa-hand-paper"></i> Captura Manual',
        'onclick': 'openCaptManual()',
    })
    toolbar.append({
        'type': 'button',
        'label': '<i class="far fa-file-excel"></i> Captura Excel',
        'onclick': 'openCaptExcel()',
    })
    toolbar.append({
        'type': 'button',
        'label': '<i class="far fa-file-word"></i> Captura Word',
        'onclick': 'openCaptWord()',
    })
    toolbar.append({
        'type': 'button',
        'label': '<i class="far fa-file-pdf"></i> Captura PDF',
        'onclick': 'openCaptPDF()',
    })
    if "POST" == request.method:
        if "update-comments" == request.POST.get('action'):
            historia.comentarios = request.POST.get('comentarios')
            historia.updated_by = usuario
            historia.save()
        elif "captura-manual" == request.POST.get('action'):
            pass
        elif "captura-excel" == request.POST.get('action'):
            pass
        elif "captura-word" == request.POST.get('action'):
            pass
        elif "captura-excel" == request.POST.get('action'):
            pass
    return render(request, 'app/cliente/historial.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Historial Laboral',
        'toolbar': toolbar,
        'cte': cte,
        'historia': historia,
    })
