from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.staticfiles import finders
from django.conf import settings
from django.db import connection

from random import shuffle
from datetime import date
import os
import json

from .forms import AccUsr
from .models import Usr
from routines.mkitsafe import valida_acceso
from routines.utils import is_mobile
from app.models import Cliente

from app.models import TaxonomiaExpediente, EstatusActividad

# Create your views here.


def index(request):
    frm = AccUsr(request.POST or None)
    if(frm.is_valid() and 'POST' == request.method):
        user = frm.login(request)
        if user is not None and user.is_active:
            auth.login(request, user)
            usuario = Usr.objects.get(id=user.pk)
            request.session['usuario'] = usuario.pk
            request.session['usuario_pic'] = "{}".format(usuario.fotografia)
            return HttpResponseRedirect(reverse('panel'))
    auth.logout(request)
    return render(request, 'index.html', {
        'is_mobile': is_mobile(request)
        })


def logout(request):
    return HttpResponseRedirect(reverse('index'))


@valida_acceso()
def item_not_found(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    return render(
        request,
        'item_no_encontrado.html', {
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Elemento no encontrado'
        }
    )


@valida_acceso()
def item_with_relations(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    return render(
        request,
        'item_con_relaciones.html', {
            'menu_main': usuario.main_menu_struct(),
            'titulo': 'Elemento relacionado'})


@valida_acceso()
def panel(request):
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    me_as_cte = None
    if Cliente.objects.filter(idusuario=usuario.pk).exists():
        me_as_cte = Cliente.objects.get(idusuario=usuario.pk)
    if "POST" == request.method:
        if "disble-alert" == request.POST.get('action'):
            alerta = usuario.alertas.get(pk=request.POST.get('alert'))
            alerta.mostrar_alerta = False
            alerta.fecha_no_mostrar = date.today()
            alerta.updated_by = usuario
            alerta.save()
    for alerta in usuario.alertas.filter(
            mostrar_alerta=True,
            fecha_alerta__lte=date.today(),
            alertado=False):
        alerta.alertado = True
        alerta.fecha_alertado = date.today()
        alerta.updated_by = usuario
        alerta.save()
    taxonomias = []
    if usuario.has_perm_or_has_perm_child('cliente.clientes_cliente'):
        taxonomias = list(TaxonomiaExpediente.objects.filter(
            mostrar_en_panel=True))
    estatus_actividad = []
    if usuario.has_perm_or_has_perm_child('cliente.clientes_cliente'):
        estatus_actividad = list(EstatusActividad.objects.filter(
            mostrar_en_panel=True))
    return render(
        request,
        'my_panel.html', {
            'menu_main': usuario.main_menu_struct(),
            'usuario': usuario.first_name,
            'alertas': usuario.alertas.filter(
                mostrar_alerta=True, fecha_alerta__lte=date.today()),
            'taxonomias': taxonomias,
            'estatus_actividad': estatus_actividad,
            'me_as_cte': me_as_cte,
        })


@valida_acceso()
def sql(request):
    'https://docs.djangoproject.com/en/2.1/topics/db/sql/'
    usuario = Usr.objects.filter(id=request.user.pk)[0]
    sql = ""
    getrows = True
    rows = False
    header = False
    error = False
    if "POST" == request.method:
        sql = request.POST.get('sql')
        getrows = request.POST.get('getrows') == 'yes'
        with connection.cursor() as cursor:
            try:
                cursor.execute(sql)
                if getrows:
                    rows = cursor.fetchall()
                    header = [c[0] for c in cursor.description]
            except Exception as e:
                error = "{}".format(e)
    return render(request, 'sql.html', {
        'menu_main': usuario.main_menu_struct(),
        'titulo': 'SQL',
        'sql': sql,
        'getrows': getrows,
        'rows': rows,
        'header': header,
        'error': error,
    })
