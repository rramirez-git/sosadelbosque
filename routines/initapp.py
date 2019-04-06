from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group

from initsys.models import Permiso, Usr
from app.models import Cliente, TaxonomiaExpediente
from .utils import clean_name


def init_app_db():
    # Perfiles
    gpos = ["Super-Administrador", "Administrador"]
    gpo_cte = Group.objects.get_or_create(name="Cliente")[0]

    # Permisos
    p_admon = Permiso.objects.get(nombre='Administración')
    p_cte = Permiso.create(
        "Clientes", "app", "cliente", 1, vista="cliente_index",
        groups=gpos)
    Permiso.create(
        "Agregar Clientes", "app", "cliente", 1, groups=gpos,
        es_operacion=True, permiso_padre=p_cte)
    Permiso.create(
        "Actualizar Clientes", "app", "cliente", 2, groups=gpos,
        es_operacion=True, permiso_padre=p_cte)
    Permiso.create(
        "Eliminar Clientes", "app", "cliente", 3, groups=gpos,
        es_operacion=True, permiso_padre=p_cte)
    p_tax = Permiso.create(
        'taxonomia', 'app', 'taxonomiaexpediente', 2,
        'Tipos de Expediente', 'taxonomia_index', False, p_admon, gpos)
    Permiso.create(
        "Agregar Taxonomia", "app", 'taxonomiaexpediente', 1,
        "Agregar Tipo de Expediente", '', True, p_tax, gpos)
    Permiso.create(
        "Actualizar Taxonomia", "app", 'taxonomiaexpediente', 2,
        "Actualizar Tipo de Expediente", '', True, p_tax, gpos)
    Permiso.create(
        "Eliminar Taxonomia", "app", 'taxonomiaexpediente', 3,
        "Eliminar Tipo de Expediente", '', True, p_tax, gpos)

    # Taxonomias

    tax = TaxonomiaExpediente.objects.get_or_create(nombre='Altas IMSS')[0]
    TaxonomiaExpediente.objects.get_or_create(nombre='Cartera 2013')
    TaxonomiaExpediente.objects.get_or_create(nombre='Trámites Pensión')
    print(tax)
    # Usuario
    pwd_cte = "sb-cte"
    usr_cte = Cliente.objects.get_or_create(
        username='cliente', first_name='Cliente',
        is_staff=False, is_active=True, is_superuser=False,
        usuario='cliente', contraseña=pwd_cte, tipo=tax,
        fecha_nacimiento=date.today(), CURP='', RFC='', NSS='', empresa='',
        fecha_afore_actual=date.today())[0]
    usr_cte.set_password(pwd_cte)
    print("Usuario Creado:\n\t   Usuario: {}\n\tContrasena: {}\n".format(
        usr_cte.username, pwd_cte))
    usr_cte.groups.set([gpo_cte])
    usr_cte.save()


