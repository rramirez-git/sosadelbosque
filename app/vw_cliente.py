from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.db.models import ProtectedError, Max, Min, Sum
from datetime import timedelta, date, datetime
from decimal import Decimal
import pandas as pd
import json
import os
import sys

from routines.mkitsafe import valida_acceso

from .models import (
    Cliente, TaxonomiaExpediente, HistoriaLaboral,
    HistoriaLaboralRegistro, HistoriaLaboralRegistroDetalle, UMA,
    DoctoGral, OpcionPension, Factoredad, Cuantiabasica)
from .forms import (
    frmCliente, frmClienteContacto, frmClienteUsuario, frmDocument,
    frmClienteObservaciones)
from initsys.forms import FrmDireccion
from initsys.models import Usr, Nota, Alerta, usr_upload_to
from routines.utils import (
    requires_jquery_ui, move_uploaded_file,
    inter_periods_days, free_days)
from app.data_utils import (
    df_load_HLRD_periodo_continuo_laborado, df_load_HLRDDay)
from routines.utils import hipernormalize


def add_nota(cte, nota, fecha_notificacion, usr):
    if "" != nota.strip():
        nota = Nota.objects.create(
            usuario=cte,
            nota=nota,
            created_by=usr,
            updated_by=usr,
        )
        if "" != fecha_notificacion:
            url = reverse('cliente_see', kwargs={'pk': cte.pk})
            link = '<a href="{}" target="_blank">{}</a>'.format(
                url, cte)
            add_alert(
                "En referencia al cliente {}:\n\n{}".format(
                    link, nota),
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
    search_value = ""
    toolbar = []
    if usuario.has_perm_or_has_perm_child('cliente.agregar_clientes_cliente'):
        toolbar.append({
            'type': 'link',
            'view': 'cliente_new',
            'label': '<i class="far fa-file"></i> Nuevo'})
    toolbar.append({'type': 'search'})
    if "POST" == request.method:
        if "search" == request.POST.get('action'):
            search_value = hipernormalize(request.POST.get('valor'))
            data = [reg
                    for reg in data if (search_value in hipernormalize(
                        reg.first_name) 
                        or search_value in hipernormalize(reg.last_name)
                        or search_value in hipernormalize(
                            reg.apellido_materno)
                        or search_value in hipernormalize(reg.CURP)
                        or search_value in hipernormalize(reg.NSS)
                        or search_value in hipernormalize(reg.RFC))
                    ]
    return render(
        request,
        'app/cliente/index.html', {
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Clientes',
            'data': data,
            'toolbar': toolbar,
            'req_ui': requires_jquery_ui(request),
            'search_value': search_value,
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
        return HttpResponseRedirect(reverse('cliente_see', kwargs={'pk': pk}))
    toolbar = []
    if usuario.has_perm_or_has_perm_child('cliente.clientes_cliente'):
        toolbar.append({
            'type': 'link',
            'view': 'cliente_index',
            'label': '<i class="fas fa-list-ul"></i> Ver todos'})
    if usuario.has_perm_or_has_perm_child('nota.notas_nota'):
        toolbar.append({
            'type': 'button',
            'label': '<i class="far fa-comment-alt"></i> Notas',
            'onclick': 'Cte.showNotasSglCte()',
        })
    if usuario.has_perm_or_has_perm_child('alerta.agregar_alertas_alerta'):
        toolbar.append({
            'type': 'button',
            'label': '<i class="far fa-bell"></i> Alerta',
            'onclick': 'Cte.showAlertsSglCte()',
        })
    if usuario.has_perm_or_has_perm_child('doctogral.agregar_documentos_docto gral'):
        toolbar.append({
            'type': 'button',
            'label': '<i class="fas fa-file-upload"></i> Adjuntar',
            'onclick': 'Cte.showFrmDoctoGral()'
        })
    if usuario.has_perm_or_has_perm_child('actividad.agregar_actividad_actividad'):
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
            'type': 'link_pk_del',
            'view': 'cliente_delete',
            'label': '<i class="far fa-trash-alt"></i> Eliminar',
            'pk': pk})
    cperms = {
        'ver_doctogral': usuario.has_perm_or_has_perm_child('doctogral.documentos_docto gral'),
        'del_doctogral': usuario.has_perm_or_has_perm_child('doctogral.eliminar_documentos_docto gral'),
        'ver_actividad': usuario.has_perm_or_has_perm_child('actividad.actividad_actividad'),
        'del_actividad': usuario.has_perm_or_has_perm_child('actividad.eliminar_actividad_actividad'),
        'ver_hl': usuario.has_perm_or_has_perm_child('historialaboral.historia_laboral_historia laboral'),
        'ver_opcpen': usuario.has_perm_or_has_perm_child('opcionpension.opciones_de_pension_opcion pension'),
    }
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
        'cperms': cperms,
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
    if usuario.has_perm_or_has_perm_child('cliente.clientes_cliente'):        
        toolbar.append({
            'type': 'link_pk',
            'view': 'cliente_see',
            'label': '<i class="far fa-eye"></i> Ver Cliente',
            'pk': cte.pk})
    if usuario.has_perm_or_has_perm_child('historialaboral.hacer_captura_manual_historia laboral'):        
        toolbar.append({
            'type': 'button',
            'label': '<i class="far fa-hand-paper"></i> C. Manual',
            'onclick': 'openCaptManual()',
        })
    if usuario.has_perm_or_has_perm_child('historialaboral.hacer_captura_desde_excel_historia laboral'):        
        toolbar.append({
            'type': 'button',
            'label': '<i class="far fa-file-excel"></i> C. Excel',
            'onclick': 'openCaptExcel()',
        })
    if usuario.has_perm_or_has_perm_child('historialaboral.hacer_captura_desde_word_historia laboral'):        
        toolbar.append({
            'type': 'button',
            'label': '<i class="far fa-file-word"></i> C. Word',
            'onclick': 'openCaptWord()',
        })
    if usuario.has_perm_or_has_perm_child('historialaboral.hacer_captura_desde_pdf_historia laboral'):        
        toolbar.append({
            'type': 'button',
            'label': '<i class="far fa-file-pdf"></i> C. PDF',
            'onclick': 'openCaptPDF()',
        })
    if "POST" == request.method:
        if "update-comments" == request.POST.get('action'):
            historia.comentarios = request.POST.get('comentarios')
            historia.uma = UMA.objects.get(pk=request.POST.get('uma'))
            historia.dias_salario_promedio = request.POST.get('dias')
            historia.tiene_esposa = "on" == request.POST.get('tiene_esposa')
            historia.numero_de_hijos = request.POST.get('numero_de_hijos')
            historia.updated_by = usuario
            historia.save()
        elif "captura-manual" == request.POST.get('action'):
            registro_patronal = request.POST.get('registro_patronal')
            empresa = request.POST.get('empresa')
            if historia.registros.filter(
                    registro_patronal=registro_patronal, empresa=empresa
                    ).exists():
                reg = historia.registros.filter(
                    registro_patronal=registro_patronal,
                    empresa=empresa)[0]
            else:
                reg = HistoriaLaboralRegistro.objects.create(
                    registro_patronal=registro_patronal,
                    empresa=empresa,
                    historia_laboral=historia,
                    created_by=usuario,
                    updated_by=usuario)
                reg.save()
            for x in range(int(request.POST.get('rows'))):
                inicio = request.POST.get('inicio_{}'.format(x + 1))
                fin = request.POST.get('fin_{}'.format(x + 1))
                salario = request.POST.get('salario_{}'.format(x + 1))
                vigente = request.POST.get('vigente_{}'.format(x + 1))
                if '' == inicio:
                    inicio = None
                if '' == fin:
                    fin = None
                if '' == salario:
                    salario = None
                else:
                    salario = Decimal(salario)
                if 'on' == vigente:
                    vigente = True
                else:
                    vigente = False
                if inicio and salario and (fin or vigente):
                    if fin:
                        HistoriaLaboralRegistroDetalle.objects.create(
                            historia_laboral_registro=reg,
                            fecha_inicial=inicio,
                            fecha_final=fin,
                            vigente=vigente,
                            salario_base=salario
                        ).save()
                    else:
                        HistoriaLaboralRegistroDetalle.objects.create(
                            historia_laboral_registro=reg,
                            fecha_inicial=inicio,
                            vigente=vigente,
                            salario_base=salario,
                            created_by=usuario,
                            updated_by=usuario
                        ).save()
            historia.reset_and_calculate_history()
        elif "captura-excel" == request.POST.get('action'):
            for x in range(int(request.POST.get('rows'))):
                registro_patronal = request.POST.get(
                    'registro_patronal_{}'.format(x + 1))
                empresa = request.POST.get('empresa_{}'.format(x + 1))
                inicio = request.POST.get('inicio_{}'.format(x + 1))
                fin = request.POST.get('fin_{}'.format(x + 1))
                salario = request.POST.get('salario_{}'.format(x + 1))
                vigente = request.POST.get('vigente_{}'.format(x + 1))
                if '' == inicio:
                    inicio = None
                if '' == fin:
                    fin = None
                if '' == salario:
                    salario = None
                else:
                    salario = Decimal(salario)
                if 'on' == vigente:
                    vigente = True
                else:
                    vigente = False
                if historia.registros.filter(
                        registro_patronal=registro_patronal,
                        empresa=empresa
                        ).exists():
                    reg = historia.registros.filter(
                        registro_patronal=registro_patronal,
                        empresa=empresa)[0]
                else:
                    reg = HistoriaLaboralRegistro.objects.create(
                        registro_patronal=registro_patronal,
                        empresa=empresa,
                        historia_laboral=historia,
                        created_by=usuario,
                        updated_by=usuario)
                    reg.save()
                if inicio and salario and (fin or vigente):
                    if fin:
                        HistoriaLaboralRegistroDetalle.objects.create(
                            historia_laboral_registro=reg,
                            fecha_inicial=inicio,
                            fecha_final=fin,
                            vigente=vigente,
                            salario_base=salario,
                            created_by=usuario,
                            updated_by=usuario
                        ).save()
                    else:
                        HistoriaLaboralRegistroDetalle.objects.create(
                            historia_laboral_registro=reg,
                            fecha_inicial=inicio,
                            vigente=vigente,
                            salario_base=salario,
                            created_by=usuario,
                            updated_by=usuario
                        ).save()
            historia.reset_and_calculate_history()
        elif "captura-word" == request.POST.get('action'):
            for x in range(int(request.POST.get('rows'))):
                registro_patronal = request.POST.get(
                    'registro_patronal_{}'.format(x + 1))
                empresa = request.POST.get('empresa_{}'.format(x + 1))
                inicio = request.POST.get('inicio_{}'.format(x + 1))
                fin = request.POST.get('fin_{}'.format(x + 1))
                salario = request.POST.get('salario_{}'.format(x + 1))
                vigente = request.POST.get('vigente_{}'.format(x + 1))
                if '' == inicio:
                    inicio = None
                if '' == fin:
                    fin = None
                if '' == salario:
                    salario = None
                else:
                    salario = Decimal(salario)
                if 'on' == vigente:
                    vigente = True
                else:
                    vigente = False
                if historia.registros.filter(
                        registro_patronal=registro_patronal, empresa=empresa
                        ).exists():
                    reg = historia.registros.filter(
                        registro_patronal=registro_patronal,
                        empresa=empresa)[0]
                else:
                    reg = HistoriaLaboralRegistro.objects.create(
                        registro_patronal=registro_patronal,
                        empresa=empresa,
                        historia_laboral=historia,
                        created_by=usuario,
                        updated_by=usuario)
                    reg.save()
                if inicio and salario and (fin or vigente):
                    if fin:
                        HistoriaLaboralRegistroDetalle.objects.create(
                            historia_laboral_registro=reg,
                            fecha_inicial=inicio,
                            fecha_final=fin,
                            vigente=vigente,
                            salario_base=salario,
                            created_by=usuario,
                            updated_by=usuario
                        ).save()
                    else:
                        HistoriaLaboralRegistroDetalle.objects.create(
                            historia_laboral_registro=reg,
                            fecha_inicial=inicio,
                            vigente=vigente,
                            salario_base=salario,
                            created_by=usuario,
                            updated_by=usuario
                        ).save()
            historia.reset_and_calculate_history()
        elif "captura-pdf" == request.POST.get('action'):
            registro_patronal = request.POST.get('registro_patronal')
            empresa = request.POST.get('empresa')
            if historia.registros.filter(
                    registro_patronal=registro_patronal, empresa=empresa
                    ).exists():
                reg = historia.registros.filter(
                    registro_patronal=registro_patronal,
                    empresa=empresa)[0]
            else:
                reg = HistoriaLaboralRegistro.objects.create(
                    registro_patronal=registro_patronal,
                    empresa=empresa,
                    historia_laboral=historia,
                    created_by=usuario,
                    updated_by=usuario)
                reg.save()
            for x in range(int(request.POST.get('rows'))):
                inicio = request.POST.get('inicio_{}'.format(x + 1))
                fin = request.POST.get('fin_{}'.format(x + 1))
                salario = request.POST.get('salario_{}'.format(x + 1))
                vigente = request.POST.get('vigente_{}'.format(x + 1))
                if '' == inicio:
                    inicio = None
                if '' == fin:
                    fin = None
                if '' == salario:
                    salario = None
                else:
                    salario = Decimal(salario)
                if 'on' == vigente:
                    vigente = True
                else:
                    vigente = False
                if inicio and salario and (fin or vigente):
                    if fin:
                        HistoriaLaboralRegistroDetalle.objects.create(
                            historia_laboral_registro=reg,
                            fecha_inicial=inicio,
                            fecha_final=fin,
                            vigente=vigente,
                            salario_base=salario,
                            created_by=usuario,
                            updated_by=usuario
                        ).save()
                    else:
                        HistoriaLaboralRegistroDetalle.objects.create(
                            historia_laboral_registro=reg,
                            fecha_inicial=inicio,
                            vigente=vigente,
                            salario_base=salario,
                            created_by=usuario,
                            updated_by=usuario
                        ).save()
            historia.reset_and_calculate_history()
        elif "update-registro" == request.POST.get('action'):
            id_data = request.POST.get('id_data')
            registro_patronal = request.POST.get('registro_patronal')
            empresa = request.POST.get('empresa')
            reg = historia.registros.get(pk=id_data)
            reg.updated_by = usuario
            reg.registro_patronal = registro_patronal
            reg.empresa = empresa
            reg.save()
        elif "update-detalle" == request.POST.get('action'):
            id_data = request.POST.get('id_data')
            inicio = request.POST.get('inicio')
            fin = request.POST.get('fin')
            salario = request.POST.get('salario')
            vigente = False
            if request.POST.get('vigente'):
                vigente = True
            reg = HistoriaLaboralRegistroDetalle.objects.get(pk=id_data)
            reg.updated_by = usuario
            reg.fecha_inicial = inicio
            reg.fecha_final = fin
            reg.salario_base = salario
            reg.vigente = vigente
            reg.save()
            historia.reset_and_calculate_history()
        return HttpResponseRedirect(reverse(
            'cliente_historia_laboral', kwargs={'pk': pk}))
    cperms = {
        'ver_dt': usuario.has_perm_or_has_perm_child('historialaboral.ver_detalle_tabular_historia laboral'),
        'ver_dg': usuario.has_perm_or_has_perm_child('historialaboral.ver_detalle_grafico_historia laboral'),
        'upd_hl': usuario.has_perm_or_has_perm_child('historialaboral.actualizar_historia_laboral_historia laboral'),
        'upd_reg': usuario.has_perm_or_has_perm_child('historialaboralregistro.actualizar_registro_historia laboral registro'),
        'del_reg': usuario.has_perm_or_has_perm_child('historialaboralregistro.eliminar_registro_historia laboral registro'),
        'upd_det': usuario.has_perm_or_has_perm_child('historialaboralregistrodetalle.actualizar_detalle_historia laboral registro detalle'),
        'del_det': usuario.has_perm_or_has_perm_child('historialaboralregistrodetalle.eliminar_detalle_historia laboral registro detalle'),
    }
    return render(request, 'app/cliente/historial.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Historial Laboral',
        'toolbar': toolbar,
        'cte': cte,
        'historia': historia,
        'umas': list(UMA.objects.all()),
        'cperms': cperms,
    })


@valida_acceso()
def delete_registro(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not HistoriaLaboralRegistro.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = HistoriaLaboralRegistro.objects.get(pk=pk)
    hl = obj.historia_laboral
    pk_cliente = hl.cliente.pk
    try:
        obj.delete()
        hl.reset_and_calculate_history()
        return HttpResponseRedirect(reverse(
            'cliente_historia_laboral', kwargs={'pk': pk_cliente}))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))


@valida_acceso()
def delete_detalle(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not HistoriaLaboralRegistroDetalle.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = HistoriaLaboralRegistroDetalle.objects.get(pk=pk)
    pk_cliente = obj.historia_laboral_registro.historia_laboral.cliente.pk
    hl = obj.historia_laboral_registro.historia_laboral
    try:
        obj.delete()
        hl.reset_and_calculate_history()
        return HttpResponseRedirect(reverse(
            'cliente_historia_laboral', kwargs={'pk': pk_cliente}))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))


@valida_acceso(['cliente.clientes_cliente'])
def historia_laboral_vista_tabular(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not HistoriaLaboral.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    historia_laboral = HistoriaLaboral.objects.get(pk=pk)
    toolbar = []
    if usuario.has_perm_or_has_perm_child('cliente.clientes_cliente'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'cliente_see',
            'label': '<i class="far fa-eye"></i> Ver Cliente',
            'pk': historia_laboral.cliente.pk})
    if usuario.has_perm_or_has_perm_child('historialaboral.historia_laboral_historia laboral'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'cliente_historia_laboral',
            'label': '<i class="fas fa-file-medical-alt"></i>'
            ' Ver Historia Laboral',
            'pk': historia_laboral.cliente.pk})
    df_pers = df_load_HLRD_periodo_continuo_laborado(historia_laboral.cliente.pk)
    df_pers[
        'historialaboralregistro'
        ] = df_pers.historialaboralregistro_pk.apply(
            lambda x: HistoriaLaboralRegistro.objects.get(pk=x).__str__()
            )
    df_pers_agg = df_pers.agg(['min', 'max', 'sum'])
    f_max = df_pers_agg.fecha_fin['max']
    f_min = df_pers_agg.fecha_inicio['min']
    dias_t = (f_max- f_min).days
    aggr_per_lab = {
        'dias_transc': dias_t,
        'dias_rec': df_pers_agg.dias_cotiz['sum'],
        'sem_rec': df_pers_agg.semanas_cotiz['sum'],
        'anios_rec': df_pers_agg.anios_cotiz['sum'],
        'dias_inac': df_pers_agg.dias_inact['sum'],
        'sem_inac': df_pers_agg.semanas_inact['sum'],
        'anios_inac': df_pers_agg.anios_inact['sum'],
        'sem_transc': round(dias_t / 7),
        'anios_transc': round(dias_t / 7) / 52,
    }
    aggr_per_lab['dias_dif'] = aggr_per_lab['dias_transc'] - aggr_per_lab['dias_rec'] - aggr_per_lab['dias_inac']
    aggr_per_lab['sem_dif'] = aggr_per_lab['sem_transc'] - aggr_per_lab['sem_rec'] - aggr_per_lab['sem_inac']
    aggr_per_lab['anios_dif'] = aggr_per_lab['anios_transc'] - aggr_per_lab['anios_rec'] - aggr_per_lab['anios_inac']

    return render(request, 'app/cliente/vista_tabular.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Detalle Laboral',
        'titulo_descripcion': historia_laboral.cliente,
        'toolbar': toolbar,
        'historia': historia_laboral,
        'aggr_per_lab': aggr_per_lab,
        'peridodos_laborados': df_pers,
    })


@valida_acceso(['cliente.clientes_cliente'])
def historia_laboral_vista_grafica(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not HistoriaLaboral.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    historia_laboral = HistoriaLaboral.objects.get(pk=pk)
    toolbar = []
    if usuario.has_perm_or_has_perm_child('cliente.clientes_cliente'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'cliente_see',
            'label': '<i class="far fa-eye"></i> Ver Cliente',
            'pk': historia_laboral.cliente.pk})
    if usuario.has_perm_or_has_perm_child('historialaboral.historia_laboral_historia laboral'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'cliente_historia_laboral',
            'label': '<i class="fas fa-file-medical-alt"></i>'
            ' Ver Historia Laboral',
            'pk': historia_laboral.cliente.pk})
    periodos = []
    dtotal = (historia_laboral.fin - historia_laboral.inicio).days
    df_periodos = df_load_HLRD_periodo_continuo_laborado(historia_laboral.cliente.pk)
    df_periodos.sort_index(ascending=False,inplace=True)
    print(df_periodos)
    for reg in historia_laboral.registros.all():
        r = {'empresa': '{}'.format(reg), 'periodos': []}
        df_pers = df_periodos[df_periodos.historialaboralregistro_pk == reg.pk]
        for p in df_pers.itertuples():
            d = (p[3] - historia_laboral.inicio).days
            r['periodos'].append({
                'dias': p[5],
                'fin': p[4].strftime('%d/%m/%Y'),
                'inicio': p[3].strftime('%d/%m/%Y'),
                'porc': p[5] * 100 / historia_laboral.dias_cotizados,
                'porc_from_start': d * 100 / dtotal,
            })
        periodos.append(r)
    return render(request, 'app/cliente/vista_grafica.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Gráfico Laboral',
        'titulo_descripcion': historia_laboral.cliente,
        'toolbar': toolbar,
        'historia': historia_laboral,
        'periods': json.dumps(periodos),
    })


@valida_acceso(['cliente.clientes_cliente'])
def delete_documento(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not DoctoGral.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = DoctoGral.objects.get(pk=pk)
    pk_cliente = obj.cliente.pk
    try:
        obj.delete()
        return HttpResponseRedirect(reverse(
            'cliente_see', kwargs={'pk': pk_cliente}))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))


def update_all_salarios(request):
    today = datetime.now()
    file_dir = os.path.join(
        settings.MEDIA_ROOT,
        'autoupdates')
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    file_dir = os.path.join(
        file_dir,
        '{}'.format(today.strftime("%Y")))
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    file_dir = os.path.join(
        file_dir,
        '{}'.format(today.strftime("%m")))
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    file_path = os.path.join(
        file_dir,
        "updates_{}.txt".format(today.strftime("%Y_%m_%d_%H_%M")))
    file = open(file_path, "a", encoding="utf8")
    regs = HistoriaLaboralRegistro.objects.filter(vigente=True)
    file.write("\n\n\nActualizacion de registros de salarios\n")
    file.write(datetime.now().strftime("%Y-%m-%d at %H:%M"))
    file.write("\n{} records to update found\n".format(regs.count()))
    for reg in regs:
        df = df_load_HLRDDay(reg.historia_laboral.cliente.pk)
        df = df[df.historialaboralregistro_pk == reg.pk]
        d = df.agg('max').fecha
        try:
            fecha_final = date(d.year, d.month, d.day)
        except AttributeError:
            fecha_final = None
        file.write("\n{}\t{:70}\t{:70}".format(
            datetime.now().strftime("%Y-%m-%d at %H:%M"),
            reg.__str__(),
            reg.historia_laboral.cliente.__str__()))
        file.flush()
        if fecha_final == reg.fin:
            file.write("Skipped")
        else:
            reg.setDates()
            file.write("Updated")
    file.close()
    return render(request, "global/html.html", {})


def update_all_salarios_complete(request):
    today = datetime.now()
    file_dir = os.path.join(
        settings.MEDIA_ROOT,
        'autoupdates_complete')
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    file_dir = os.path.join(
        file_dir,
        '{}'.format(today.strftime("%Y")))
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    file_dir = os.path.join(
        file_dir,
        '{}'.format(today.strftime("%m")))
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    file_path = os.path.join(
        file_dir,
        "updates_{}.txt".format(today.strftime("%Y_%m_%d_%H_%M")))
    file = open(file_path, "a", encoding="utf8")
    regs = HistoriaLaboralRegistro.objects.all()
    file.write("\n\n\nActualizacion de registros de salarios\n")
    file.write(datetime.now().strftime("%Y-%m-%d at %H:%M"))
    file.write("\n{} records to update found\n".format(regs.count()))
    for reg in regs:
        df = df_load_HLRDDay(reg.historia_laboral.cliente.pk)
        df = df[df.historialaboralregistro_pk == reg.pk]
        d = df.agg('max').fecha
        try:
            fecha_final = date(d.year, d.month, d.day)
        except AttributeError:
            fecha_final = None
        file.write("\n{}\t{:70}\t{:70}".format(
            datetime.now().strftime("%Y-%m-%d at %H:%M"),
            reg.__str__(),
            reg.historia_laboral.cliente.__str__()))
        file.flush()
        if fecha_final == reg.fin:
            file.write("Skipped")
        else:
            reg.setDates()
            file.write("Updated")
    file.close()
    return render(request, "global/html.html", {})


@valida_acceso(['opcionpension.opciones_de_pension_opcion pension'])
def pensiones_list(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Cliente.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    cte = Cliente.objects.get(pk=pk)
    if HistoriaLaboral.objects.filter(cliente=cte).exists():
        historia = HistoriaLaboral.objects.get(cliente=cte)
    else:
        historia = HistoriaLaboral.objects.create(
            cliente=cte, created_by=usuario, updated_by=usuario)
        historia.save()
    toolbar = []
    if usuario.has_perm_or_has_perm_child('opcionpension.agregar_opcion_de_pension_opcion pension'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'cliente_pension_new',
            'label': '<i class="far fa-file"></i> Nuevo',
            'pk': pk})
    if usuario.has_perm_or_has_perm_child('cliente.clientes_cliente'):
        toolbar.append({
            'type': 'link_pk',
            'view': 'cliente_see',
            'label': '<i class="far fa-eye"></i> Ver Cliente',
            'pk': pk})
    cperms = {
        'del_opc': usuario.has_perm_or_has_perm_child('opcionpension.eliminar_opcion_de_pension_opcion pension'),
        'set_opc': usuario.has_perm_or_has_perm_child('opcionpension.seleccionar_opcion_de_pension_opcion pension'),
        'ust_opc': usuario.has_perm_or_has_perm_child('opcionpension.deseleccionar_opcion_de_pension_opcion pension'),
    }
    return render(request, 'app/cliente/pension_index.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Opciones de Pension',
        'titulo_descripcion': cte,
        'req_ui': requires_jquery_ui(request),
        'read_only': True,
        'toolbar': toolbar,
        'cliente': cte,
        'historia': historia,
        'umas': list(UMA.objects.all()),
        'factoresedad': list(Factoredad.objects.all()),
        'cperms': cperms,
    })


@valida_acceso(['opcionpension.agregar_opcion_de_pension_opcion pension'])
def pensiones_new(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not Cliente.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
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
        'pk': pk})
    toolbar.append({
        'type': 'link_pk',
        'view': 'cliente_pension_index',
        'label': '<i class="fas fa-list-ul"></i> Ver Opciones de Pensión',
        'pk': pk})
    if "POST" == request.method:
        opcion = OpcionPension.objects.create(
            historia_laboral=historia,
            seleccionada=request.POST.get('seleccionada') == "on",
            uma_anio=request.POST.get('uma_anio'),
            uma_valor=request.POST.get('uma_valor'),
            salario_promedio=request.POST.get('salario_promedio'),
            salario_promedio_mensual=request.POST.get('salario_promedio_mensual'),
            dias_calculo_saldo_promedio=historia.dias_salario_promedio,
            semanas_cotizadas=request.POST.get('semanas_cotizadas'),
            porcentaje_cuantia_basica=request.POST.get('porcentaje_cuantia_basica'),
            porcentaje_incremento_anual=request.POST.get('porcentaje_incremento_anual'),
            edad=request.POST.get('edad'),
            porcentaje_factor_edad=request.POST.get('porcentaje_factor_edad'),
            porcentaje_cuantia_basica_incremento=request.POST.get('porcentaje_cuantia_basica_incremento'),
            factor_actualizacion=request.POST.get('factor_actualizacion'),
            porcentaje_esposa=request.POST.get('porcentaje_esposa'),
            porcentaje_hijos=request.POST.get('porcentaje_hijos'),
            porcentaje_asignaciones_familiares=request.POST.get('porcentaje_asignaciones_familiares'),
            pension_mensual_calculada=request.POST.get('pension_mensual_calculada'),
            porcentaje_de_salario_promedio=request.POST.get('porcentaje_de_salario_promedio'),
            comentarios=request.POST.get('comentarios'),
            created_by=usuario,
            updated_by=usuario,
        )
        return HttpResponseRedirect(reverse(
            'cliente_pension_index', kwargs={'pk': cte.pk}
        ))
    else:
        opcion = {
            'created_at': date.today(),
            'uma_anio': historia.uma.año,
            'uma_valor': historia.uma.valor,
            'semanas_cotizadas': historia.semanas_cotizadas,
            'salario_promedio': historia.agg_salario()['salario_promedio'],
            'edad': cte.edad,
            'factor_actualizacion': historia.factor_de_actualizacion,
            'porcentaje_esposa': historia.tiene_esposa * 15,
            'porcentaje_hijos': historia.numero_de_hijos * 10,
        }
    return render(request, 'app/cliente/pension_new.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'Nueva Opciones de Pension',
        'titulo_descripcion': cte,
        'req_ui': requires_jquery_ui(request),
        'toolbar': toolbar,
        'cliente': cte,
        'historia': historia,
        'umas': list(UMA.objects.all()),
        'factoresedad': list(Factoredad.objects.all()),
        'cbis': json.dumps([{
            'inicio': float(cbi.salario_inicio),
            'fin': float(cbi.salario_fin),
            'cb': float(cbi.porcentaje_de_cuantia_basica),
            'i': float(cbi.porcentaje_de_incremento_anual),
            } for cbi in Cuantiabasica.objects.all()]),
        'opcion': opcion,
    })


@valida_acceso(['opcionpension.eliminar_opcion_de_pension_opcion pension'])
def pensiones_delete(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not OpcionPension.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = OpcionPension.objects.get(pk=pk)
    pk_cliente = obj.historia_laboral.cliente.pk
    try:
        obj.delete()
        return HttpResponseRedirect(reverse(
            'cliente_pension_index', kwargs={'pk': pk_cliente}))
    except ProtectedError:
        return HttpResponseRedirect(reverse('item_con_relaciones'))


@valida_acceso(['opcionpension.seleccionar_opcion_de_pension_opcion pension'])
def pensiones_select(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not OpcionPension.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = OpcionPension.objects.get(pk=pk)
    pk_cliente = obj.historia_laboral.cliente.pk
    obj.seleccionada = True
    obj.updated_by = usuario
    obj.save()
    return HttpResponseRedirect(reverse(
        'cliente_pension_index', kwargs={'pk': pk_cliente}))


@valida_acceso(['opcionpension.deseleccionar_opcion_de_pension_opcion pension'])
def pensiones_unselect(request, pk):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    if not OpcionPension.objects.filter(pk=pk).exists():
        return HttpResponseRedirect(reverse('item_no_encontrado'))
    obj = OpcionPension.objects.get(pk=pk)
    pk_cliente = obj.historia_laboral.cliente.pk
    obj.seleccionada = False
    obj.updated_by = usuario
    obj.save()
    return HttpResponseRedirect(reverse(
        'cliente_pension_index', kwargs={'pk': pk_cliente}))