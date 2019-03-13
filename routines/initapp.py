from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group

from initsys.models import Permiso, Usr
from app.models import Cliente
from .utils import clean_name


def init_app_db():
    # Perfiles
    gpos = ["Super-Administrador", "Administrador"]
    gpo_cte = Group.objects.create(name="Cliente")

    # Permisos
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

    # Usuario
    pwd_cte = "sb-cte"
    usr_cte = Cliente.objects.create(
        username='cliente', first_name='Cliente',
        is_staff=False, is_active=True, is_superuser=False,
        usuario='cliente', contraseña=pwd_cte)
    usr_cte.set_password(pwd_cte)
    print("Usuario Creado:\n\t   Usuario: {}\n\tContrasena: {}\n".format(
        usr_cte.username, pwd_cte))
    usr_cte.groups.set([gpo_cte])
    usr_cte.save()

  