from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group

from initsys.models import Permiso, Usr, Setting, setting_upload_to
from .utils import clean_name


def init_db():
    """
    Inicializacion de la base de datos, permisos minimos de seguridad.

    Ejecutar desde shell

    return None
    """
    for e in Permiso.objects.all():
        e.delete()
    for e in Group.objects.all():
        e.delete()
    for e in Usr.objects.all():
        e.delete()
    for e in Setting.objects.all():
        e.delete()

    # Content Types
    ct_perm = ContentType.objects.get(app_label="initsys", model="permiso")
    ct_usr = ContentType.objects.get(app_label="initsys", model="usr")
    ct_user = ContentType.objects.get(app_label="auth", model="user")
    ct_gpo = ContentType.objects.get(app_label="auth", model="group")
    ct_permission = ContentType.objects.get(
        app_label="auth", model="permission")
    ct_setting = ContentType.objects.get(
        app_label="initsys", model="setting")

    # Permisos
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

    # Perfiles
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

    # Usuarios
    pwd_sadmin = "sb-sadmin"
    pwd_admin = "sb-admin"
    usr_sadmin = Usr.objects.create(
        username='superadmin', first_name='Super Administrador',
        is_staff=True, is_active=True, is_superuser=True,
        usuario='superadmin', contraseña=pwd_sadmin)
    usr_sadmin.set_password(pwd_sadmin)
    print("Usuario Creado:\n\t   Usuario: {}\n\tContrasena: {}\n".format(
        usr_sadmin.username, pwd_sadmin))
    usr_sadmin.groups.set([gpo_sadmin])
    usr_sadmin.save()
    usr_admin = Usr.objects.create(
        username='admin', first_name='Administrador',
        is_staff=False, is_active=True, is_superuser=False,
        usuario='admin', contraseña=pwd_admin)
    usr_admin.set_password(pwd_admin)
    usr_admin.groups.set([gpo_admin])
    usr_admin.save()
    print("Usuario Creado:\n\t   Usuario: {}\n\tContrasena: {}\n".format(
        usr_admin.username, pwd_admin))

    # Settings
    Setting.objects.create(
        seccion="01 General",
        nombre="favicon",
        nombre_para_mostrar="Icono del Sitio",
        valor="{}/{}".format(setting_upload_to, "favicon.png"),
        tipo="PICTURE",
        es_multiple=False,
        created_by=usr_sadmin
    )
    Setting.objects.create(
        seccion="01 General",
        nombre="main_menu_icon",
        nombre_para_mostrar="Logo Menú Principal",
        valor="{}/{}".format(setting_upload_to, "logo_main.png"),
        tipo="PICTURE",
        es_multiple=False,
        created_by=usr_sadmin
    )
    Setting.objects.create(
        seccion="01 General",
        nombre="splash_icon",
        nombre_para_mostrar="Logo Página Principal",
        valor="{}/{}".format(setting_upload_to, "logo_splash.png"),
        tipo="PICTURE",
        es_multiple=False,
        created_by=usr_sadmin
    )
    Setting.objects.create(
        seccion="01 General",
        nombre="site_name",
        nombre_para_mostrar="Nombre del Sitio",
        valor="..:: Sosa del Bosque ::..",
        tipo="STRING",
        es_multiple=False,
        created_by=usr_sadmin
    )
    Setting.objects.create(
        seccion="01 General",
        nombre="footer_text",
        nombre_para_mostrar="Pie de Página",
        valor='Sosa del Bosque © 2019 | Todos l'
        'os Derechos Reservados | <a href="#" onclick="App.showPrivacyPoli'
        'cy()" style="color: #ffffff">Política de Privacidad</a>',
        tipo="STRING",
        es_multiple=False,
        created_by=usr_sadmin
    )
    Setting.objects.create(
        seccion="01 General",
        nombre="privacy_policy",
        nombre_para_mostrar="Política de Privacidad",
        valor="""Aviso de Privacidad

Los principios siguientes marcan nuestra perspectiva respecto a la integridad y privacidad de sus datos:

1) Apreciamos su confianza al brindarnos sus datos personales, mismos que se emplearan justa y dignamente.
2) El propietario de los datos tiene derecho a tener información clara (y nosotros la obligación de brindarla) de como manipularemos su información personal a través de la transparencia acerca de la información recolectada, su procesamiento, con quien es compartida y a quien contactar en caso de tener dudas o inconformidades.
3) Emplearemos procesos razonables para proteger su información y evitar el uso indebido de esta.

-----------------

Con base en los artículos 15 y 16 de la Ley Federal de Protección de Datos Personales en Posesión de Particulares hacemos de su conocimiento que TocaTres, con domicilio en la Ciudad de México, es responsable de recabar, emplear y proteger sus datos personales.

Sus datos personales se emplearan para:

1) Proveer y dar seguimiento a sus productos y servicios.
2) Establecer comunicación sobre nuevos servicios o productos relacionados con los suyos.
3) Comunicarle sobre cambios en los mismos.
4) Realizar peritajes periódicos a sus productos y servicios para evaluar y mejorar la calidad de los mismos.
5) Evaluar la calidad del servicio
6) Para dar cumplimiento a las obligaciones que hemos contraído con usted.

De igual forma le notificamos que no se manejan datos categorizados como sensibles y que para ejercer su derecho al acceso, corrección o cancelación de sus datos personales es necesario que envié la solicitud en los Términos que marca la Ley en su Art. 29 al Departamento de Administración y Atención al cliente, responsable de la Protección de Datos Personales, ubicado en la Ciudad de México, o bien, se comunique al teléfono XXXXXXXXXX o vía correo electrónico a XXXXXXXXXX, el cual solicitamos confirme vía telefónica para garantizar su correcta recepción.

Así mismo se le informa que sus datos no se transfieren a terceras personas.

Nota: Cualquier actualización a este Aviso de Privacidad sera consultable en http://www.XXXXXXXXXX

Los datos personales requeridos y recolectados son:

1) Nombre completo
2) Teléfono fijo y/o celular
3) Correo electrónico
4) Dirección""",
        tipo="TEXT",
        es_multiple=False,
        created_by=usr_sadmin
    )

    Setting.objects.create(
        seccion="02_PaginaPrincipal_Bloque_1",
        nombre="b1_imagen",
        nombre_para_mostrar="Imagen",
        valor='',
        tipo="PICTURE",
        es_multiple=False,
        created_by=usr_sadmin
    )
    Setting.objects.create(
        seccion="02_PaginaPrincipal_Bloque_1",
        nombre="b1_line1",
        nombre_para_mostrar="Linea 1",
        valor='Asesores y Gestores en:',
        tipo="STRING",
        es_multiple=False,
        created_by=usr_sadmin
    )
    Setting.objects.create(
        seccion="02_PaginaPrincipal_Bloque_1",
        nombre="b1_line2",
        nombre_para_mostrar="Linea 2",
        valor='Pensiones IMSS, INFONAVIT y Afore',
        tipo="STRING",
        es_multiple=False,
        created_by=usr_sadmin
    )
    Setting.objects.create(
        seccion="02_PaginaPrincipal_Bloque_1",
        nombre="b1_Texto",
        nombre_para_mostrar="Descripción",
        valor='Sosa del Bosque somos un grupo de Asesores y Gestores con más de diez años de experiencia especializados en el Sistema de Ahorro para el Retiro, IMSS, INFONAVIT y AFORE, nos enfocamos en la solución de los problemas que tengan los trabajadores dentro del sistema, prevención de procedimientos y agilización de trámites para que a todos nuestros clientes les sea reconocido y dado el beneficio adquirido en forma de pensión por todos los años de trabajo.',
        tipo="TEXT",
        es_multiple=False,
        created_by=usr_sadmin
    )
    
    Setting.objects.create(
        seccion="02_PaginaPrincipal_Bloque_2",
        nombre="b2_Title",
        nombre_para_mostrar="Título",
        valor='¿Quienes somos?',
        tipo="STRING",
        es_multiple=False,
        created_by=usr_sadmin
    )
    Setting.objects.create(
        seccion="02_PaginaPrincipal_Bloque_2",
        nombre="b2_Texto",
        nombre_para_mostrar="Texto",
        valor="""Sosa del Bosque somos un grupo de Asesores y Gestores con más de diez años de experiencia especializados en el Sistema de Ahorro para el Retiro, IMSS, INFONAVIT y AFORE, nos enfocamos en la solución de los problemas que tengan los trabajadores dentro del sistema, prevención de procedimientos y agilización de trámites para que a todos nuestros clientes les sea reconocido y dado el beneficio adquirido en forma de pensión por todos los años de trabajo.

La experiencia y trayectoria de nuestros integrantes nos permite diseñar un plan a la medida de cada trabajador como estrategia de retiro de la vida laboral y obtener la mayor pensión de acuerdo a su perfil.

En Sosa del Bosque nos esmeramos en cumplir con todos y cada uno de nuestros clientes los compromisos adquiridos en tiempo y forma de modo tal que tengan la seguridad, garantía y tranquilidad que necesitan en esta etapa tan importante de transición y nueva forma de vida.""",
        tipo="STRING",
        es_multiple=False,
        created_by=usr_sadmin
    )

init_db()
print("Done...")