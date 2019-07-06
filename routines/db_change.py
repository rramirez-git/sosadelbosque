from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group

from datetime import date

from initsys.models import Permiso, Usr, Setting, setting_upload_to
from app.models import (
    Cliente, TaxonomiaExpediente, HistoriaLaboralRegistro)
from .utils import clean_name

def initsys_fn_upd():
    Permiso.objects.all().delete()
    Group.objects.all().delete()
    Usr.objects.all().delete()
    Setting.objects.all().delete()

    ct_perm = ContentType.objects.get(app_label="initsys", model="permiso")
    ct_usr = ContentType.objects.get(app_label="initsys", model="usr")
    ct_user = ContentType.objects.get(app_label="auth", model="user")
    ct_gpo = ContentType.objects.get(app_label="auth", model="group")
    ct_permission = ContentType.objects.get(
        app_label="auth", model="permission")
    ct_setting = ContentType.objects.get(
        app_label="initsys", model="setting")

    perm_conf = Permiso.objects.create(
        nombre='Configuracion',
        name='Configuracion',
        codename="{}_{}".format(clean_name("Configuracion"), ct_perm),
        mostrar_como='Configuracion',
        es_operacion=False,
        posicion=99,
        permiso_padre=None,
        content_type=ct_perm
    )
    perm_gpo = Permiso.objects.create(
        nombre='Perfiles',
        name='Perfiles',
        codename="{}_{}".format(clean_name("Perfiles"), ct_gpo),
        mostrar_como='Perfiles',
        vista='perfil_index',
        es_operacion=False,
        posicion=1,
        permiso_padre=perm_conf,
        content_type=ct_gpo
    )
    Permiso.objects.create(
        nombre='Agregar Perfiles',
        name='Agregar Perfiles',
        codename="{}_{}".format(clean_name("Agregar Perfiles"), ct_gpo),
        mostrar_como='Agregar Perfiles',
        es_operacion=True,
        posicion=1,
        permiso_padre=perm_gpo,
        content_type=ct_gpo
    )
    Permiso.objects.create(
        nombre='Actualizar Perfiles',
        name='Actualizar Perfiles',
        codename="{}_{}".format(clean_name("Actualizar Perfiles"), ct_gpo),
        mostrar_como='Actualizar Perfiles',
        es_operacion=True,
        posicion=2,
        permiso_padre=perm_gpo,
        content_type=ct_gpo
    )
    Permiso.objects.create(
        nombre='Eliminar Perfiles',
        name='Eliminar Perfiles',
        codename="{}_{}".format(clean_name("Eliminar Perfiles"), ct_gpo),
        mostrar_como='Eliminar Perfiles',
        es_operacion=True,
        posicion=3,
        permiso_padre=perm_gpo,
        content_type=ct_gpo
    )
    perm_perm = Permiso.objects.create(
        nombre='Permisos',
        name='Permisos',
        codename="{}_{}".format(clean_name("Permisos"), ct_perm),
        mostrar_como='Permisos',
        vista='permiso_index',
        es_operacion=False,
        posicion=2,
        permiso_padre=perm_conf,
        content_type=ct_perm
    )
    Permiso.objects.create(
        nombre='Agregar Permisos',
        name='Agregar Permisos',
        codename="{}_{}".format(clean_name("Agregar Permisos"), ct_perm),
        mostrar_como='Agregar Permisos',
        es_operacion=True,
        posicion=1,
        permiso_padre=perm_perm,
        content_type=ct_perm
    )
    Permiso.objects.create(
        nombre='Actualizar Permisos',
        name='Actualizar Permisos',
        codename="{}_{}".format(
            clean_name("Actualizar Permisos"), ct_perm),
        mostrar_como='Actualizar Permisos',
        es_operacion=True,
        posicion=2,
        permiso_padre=perm_perm,
        content_type=ct_perm
    )
    Permiso.objects.create(
        nombre='Eliminar Permisos',
        name='Eliminar Permisos',
        codename="{}_{}".format(clean_name("Eliminar Permisos"), ct_perm),
        mostrar_como='Eliminar Permisos',
        es_operacion=True,
        posicion=3,
        permiso_padre=perm_perm,
        content_type=ct_perm
    )
    Permiso.objects.create(
        nombre='Perms',
        name='Perms',
        codename="{}_{}".format(clean_name("Perms"), ct_permission),
        mostrar_como='Perms',
        vista='permission_index',
        es_operacion=False,
        posicion=4,
        permiso_padre=perm_perm,
        content_type=ct_permission
    )
    perm_setting = Permiso.objects.create(
        nombre="Administrar_Settings",
        name="Administrar_Settings",
        codename="{}_{}".format(
            clean_name("Administrar_Settings"), ct_setting),
        mostrar_como="Administrar Settings",
        vista="setting_index",
        es_operacion=False,
        posicion=3,
        permiso_padre=perm_conf,
        content_type=ct_setting
    )
    Permiso.objects.create(
        nombre="Agregar Settings",
        name="Agregar Settings",
        codename="{}_{}".format(
            clean_name("Agregar Settings"), ct_setting),
        mostrar_como="Agregar Settings",
        es_operacion=True,
        posicion=1,
        permiso_padre=perm_setting,
        content_type=ct_setting
    )
    Permiso.objects.create(
        nombre="Actualizar Settings",
        name="Actualizar Settings",
        codename="{}_{}".format(
            clean_name("Actualizar Settings"), ct_setting),
        mostrar_como="Actualizar Settings",
        es_operacion=True,
        posicion=2,
        permiso_padre=perm_setting,
        content_type=ct_setting
    )
    Permiso.objects.create(
        nombre="Eliminar Settings",
        name="Eliminar Settings",
        codename="{}_{}".format(
            clean_name("Eliminar Settings"), ct_setting),
        mostrar_como="Eliminar Settings",
        es_operacion=True,
        posicion=3,
        permiso_padre=perm_setting,
        content_type=ct_setting
    )
    Permiso.objects.create(
        nombre="Settings",
        name="Settings",
        codename="{}_{}".format(clean_name("Settings"), ct_setting),
        mostrar_como="Parámetros de Sistema",
        vista="setting_value",
        es_operacion=False,
        posicion=4,
        permiso_padre=perm_conf,
        content_type=ct_setting
    )
    perm_adm = Permiso.objects.create(
        nombre='Administración',
        name='Administración',
        codename="{}_{}".format(clean_name("Administración"), ct_perm),
        mostrar_como='Administración',
        es_operacion=False,
        posicion=98,
        permiso_padre=None,
        content_type=ct_perm
    )
    perm_usrs = Permiso.objects.create(
        nombre='Usuarios',
        name='Usuarios',
        codename="{}_{}".format(clean_name("Usuarios"), ct_usr),
        mostrar_como='Usuarios',
        vista='usuario_index',
        es_operacion=False,
        posicion=1,
        permiso_padre=perm_adm,
        content_type=ct_usr
    )
    Permiso.objects.create(
        nombre='Agregar Usuarios',
        name='Agregar Usuarios',
        codename="{}_{}".format(clean_name("Agregar Usuarios"), ct_usr),
        mostrar_como='Agregar Usuarios',
        es_operacion=True,
        posicion=1,
        permiso_padre=perm_usrs,
        content_type=ct_usr
    )
    Permiso.objects.create(
        nombre='Actualizar Usuarios',
        name='Actualizar Usuarios',
        codename="{}_{}".format(clean_name("Actualizar Usuarios"), ct_usr),
        mostrar_como='Actualizar Usuarios',
        es_operacion=True,
        posicion=2,
        permiso_padre=perm_usrs,
        content_type=ct_usr
    )
    Permiso.objects.create(
        nombre='Eliminar Usuarios',
        name='Eliminar Usuarios',
        codename="{}_{}".format(clean_name("Eliminar Usuarios"), ct_usr),
        mostrar_como='Eliminar Usuarios',
        es_operacion=True,
        posicion=3,
        permiso_padre=perm_usrs,
        content_type=ct_usr
    )
    Permiso.objects.create(
        nombre='Users',
        name='Users',
        codename="{}_{}".format(clean_name("Users"), ct_user),
        mostrar_como='Users',
        vista='user_index',
        es_operacion=False,
        posicion=4,
        permiso_padre=perm_usrs,
        content_type=ct_user
    )

    print("Main perms done")

    gpo_sadmin = Group.objects.create(name="Super-Administrador")
    gpo_sadmin.permissions.set(list(Permiso.objects.all()))
    gpo_admin = Group.objects.create(name="Administrador")
    gpo_admin.permissions.set(list(Permiso.objects.filter(
        codename__in=[
            'configuracion_permiso', 'perfiles_group',
            'agregar_perfiles_group', 'actualizar_perfiles_group',
            'eliminar_perfiles_group', 'administracion_permiso',
            'usuarios_user', 'agregar_usuarios_user',
            'actualizar_usuarios_user', 'eliminar_usuarios_user',
            'settings_setting']
    )))

    print("Grupos Creados")


def app_fn_upd():
    gpos = ["Super-Administrador", "Administrador"]
    gpo_cte = Group.objects.get_or_create(name="Cliente")[0]

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

    

    p_tipodocto = Permiso.create(
        "Tipos de Documento", "app", "tipodocumento", 4, None,
        "tipodocumento_index", False, p_admon, gpos)
    Permiso.create(
        "Agregar Tipo de Documento", "app", "tipodocumento", 1,
        es_operacion=True, permiso_padre=p_tipodocto, groups=gpos)
    Permiso.create(
        "Actualizar Tipo de Documento", "app", "tipodocumento", 2,
        es_operacion=True, permiso_padre=p_tipodocto, groups=gpos)
    Permiso.create(
        "Eliminar Tipo de Documento", "app", "tipodocumento", 3,
        es_operacion=True, permiso_padre=p_tipodocto, groups=gpos)

    p_estatusactividad = Permiso.create(
        "Estatus de Actividad", "app", "estatusactividad", 5, None,
        "estatusactividad_index", False, p_admon, gpos)
    Permiso.create(
        "Agregar Estatus de Actividad", "app", "estatusactividad", 1,
        es_operacion=True, permiso_padre=p_estatusactividad, groups=gpos)
    Permiso.create(
        "Actualizar Estatus de Actividad", "app", "estatusactividad", 2,
        es_operacion=True, permiso_padre=p_estatusactividad, groups=gpos)
    Permiso.create(
        "Eliminar Estatus de Actividad", "app", "estatusactividad", 3,
        es_operacion=True, permiso_padre=p_estatusactividad, groups=gpos)

    p_tipoactividad = Permiso.create(
        "Tipos de Actividad", "app", "tipoactividad", 6, None,
        "tipoactividad_index", False, p_admon, gpos)
    Permiso.create(
        "Agregar Tipo de Actividad", "app", "tipoactividad", 1,
        es_operacion=True, permiso_padre=p_tipoactividad, groups=gpos)
    Permiso.create(
        "Actualizar Tipo de Actividad", "app", "tipoactividad",  2,
        es_operacion=True, permiso_padre=p_tipoactividad, groups=gpos)
    Permiso.create(
        "Eliminar Tipo de Actividad", "app", "tipoactividad", 3,
        es_operacion=True, permiso_padre=p_tipoactividad, groups=gpos)

    p_externo = Permiso.create(
        "Externos", "app", "externo", 7, "Personas Externas",
        "externo_index", False, p_admon, gpos)
    Permiso.create(
        "Agregar Externo", "app", "externo", 1, "Agregar Persona Externa",
        '', True, p_externo, gpos)
    Permiso.create(
        "Actualizar Externo", "app", "externo", 2,
        "Actualizar Persona Externa", '', True, p_externo, gpos)
    Permiso.create(
        "Eliminar Externo", "app", "externo", 3,
        "Eliminar Persona Externa", '', True, p_externo, gpos)

    p_report = Permiso.create(
        "Reportes", "auth", "permission", 2,
        groups=gpos)
    Permiso.create(
        "Maestro de Clientes", "auth", "permission", 1,
        vista='cliente_reporte_maestro', permiso_padre=p_report,
        groups=gpos)
    Permiso.create(
        "Maestro de Actividades", "auth", "permission", 2,
        vista='actividad_reporte_maestro', permiso_padre=p_report,
        groups=gpos)

    p_uma = Permiso.create(
        "UMA", "app", "uma", 8, "Unidad de Medida y Actualización (UMA)",
        'uma_index', False, p_admon, gpos)
    Permiso.create(
        "Agregar UMA", "app", "uma", 1, es_operacion=True,
        permiso_padre=p_uma, groups=gpos)
    Permiso.create(
        "Actualizar UMA", "app", "uma", 2, es_operacion=True,
        permiso_padre=p_uma, groups=gpos)
    Permiso.create(
        "Eliminar UMA", "app", "uma", 3, es_operacion=True,
        permiso_padre=p_uma, groups=gpos)

    p_cb = Permiso.create(
        "CuantiaBasica", "app", "cuantiabasica", 9,
        "Cuantía Básica e Incremento Anual", "cuantiabasica_index", False,
        p_admon, gpos)
    Permiso.create(
        "Agregar CuantiaBasica", "app", "cuantiabasica", 1,
        es_operacion=True, permiso_padre=p_cb, groups=gpos)
    Permiso.create(
        "Actualizar CuantiaBasica", "app", "cuantiabasica", 2,
        es_operacion=True, permiso_padre=p_cb, groups=gpos)
    Permiso.create(
        "Eliminar CuantiaBasica", "app", "cuantiabasica", 3,
        es_operacion=True, permiso_padre=p_cb, groups=gpos)
    p_fe = Permiso.create(
        "FactorEdad", "app", "factoredad", 10,
        "Porcentaje de Factor de Edad", "factoredad_index", False,
        p_admon, gpos)
    Permiso.create(
        "Agregar FactorEdad", "app", "factoredad", 1,
        es_operacion=True, permiso_padre=p_fe, groups=gpos)
    Permiso.create(
        "Actualizar FactorEdad", "app", "factoredad", 2,
        es_operacion=True, permiso_padre=p_fe, groups=gpos)
    Permiso.create(
        "Eliminar FactorEdad", "app", "factoredad", 3,
        es_operacion=True, permiso_padre=p_fe, groups=gpos)

    print("Perms done")

initsys_fn_upd()
app_fn_upd()
