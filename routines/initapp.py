from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group

from initsys.models import Permiso, Usr
from app.models import (
    Cliente, TaxonomiaExpediente, HistoriaLaboralRegistro)
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


def upd190406():
    gpos = ["Super-Administrador", "Administrador"]
    p_admon = Permiso.objects.get(nombre='Administración')

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


def upd190528():
    gpos = ["Super-Administrador", "Administrador"]
    p_admon = Permiso.objects.get(nombre='Administración')

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

    print("Permisos creados upd190528")


def upd190604():
    gpos = ["Super-Administrador", "Administrador"]
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

    print("Permisos creados upd190604")


def upd190617():
    from app.models import UMA
    gpos = ["Super-Administrador", "Administrador"]
    p_admon = Permiso.objects.get(nombre='Administración')
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

    print("Permisos creados upd190617")

    UMA.objects.all().delete()
    UMA.objects.create(año=2016, valor=73.04)
    UMA.objects.create(año=2017, valor=75.49)
    UMA.objects.create(año=2018, valor=80.60)
    UMA.objects.create(año=2019, valor=84.49)

    print("Unidades de medida y actualizacion creadas")


def upd190619():
    from app.models import Cuantiabasica, Factoredad
    gpos = ["Super-Administrador", "Administrador"]
    p_admon = Permiso.objects.get(nombre='Administración')
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

    Cuantiabasica.objects.all().delete()
    Cuantiabasica.objects.create(
        salario_inicio=0, salario_fin=1,
        porcentaje_de_cuantia_basica=80,
        porcentaje_de_incremento_anual=0.563)
    Cuantiabasica.objects.create(
        salario_inicio=1.0001, salario_fin=1.25,
        porcentaje_de_cuantia_basica=77.11,
        porcentaje_de_incremento_anual=0.814)
    Cuantiabasica.objects.create(
        salario_inicio=1.2501, salario_fin=1.5,
        porcentaje_de_cuantia_basica=58.18,
        porcentaje_de_incremento_anual=1.178)
    Cuantiabasica.objects.create(
        salario_inicio=1.5001, salario_fin=1.75,
        porcentaje_de_cuantia_basica=49.23,
        porcentaje_de_incremento_anual=1.43)
    Cuantiabasica.objects.create(
        salario_inicio=1.7501, salario_fin=2,
        porcentaje_de_cuantia_basica=42.67,
        porcentaje_de_incremento_anual=1.615)
    Cuantiabasica.objects.create(
        salario_inicio=2.0001, salario_fin=2.25,
        porcentaje_de_cuantia_basica=37.65,
        porcentaje_de_incremento_anual=1.756)
    Cuantiabasica.objects.create(
        salario_inicio=2.2501, salario_fin=2.5,
        porcentaje_de_cuantia_basica=33.68,
        porcentaje_de_incremento_anual=1.868)
    Cuantiabasica.objects.create(
        salario_inicio=2.5001, salario_fin=2.75,
        porcentaje_de_cuantia_basica=30.48,
        porcentaje_de_incremento_anual=1.958)
    Cuantiabasica.objects.create(
        salario_inicio=2.7501, salario_fin=3,
        porcentaje_de_cuantia_basica=27.83,
        porcentaje_de_incremento_anual=2.033)
    Cuantiabasica.objects.create(
        salario_inicio=3.0001, salario_fin=3.25,
        porcentaje_de_cuantia_basica=25.6,
        porcentaje_de_incremento_anual=2.096)
    Cuantiabasica.objects.create(
        salario_inicio=3.2501, salario_fin=3.5,
        porcentaje_de_cuantia_basica=23.7,
        porcentaje_de_incremento_anual=2.149)
    Cuantiabasica.objects.create(
        salario_inicio=3.5001, salario_fin=3.75,
        porcentaje_de_cuantia_basica=22.07,
        porcentaje_de_incremento_anual=2.195)
    Cuantiabasica.objects.create(
        salario_inicio=3.7501, salario_fin=4,
        porcentaje_de_cuantia_basica=20.65,
        porcentaje_de_incremento_anual=2.235)
    Cuantiabasica.objects.create(
        salario_inicio=4.0001, salario_fin=4.25,
        porcentaje_de_cuantia_basica=19.39,
        porcentaje_de_incremento_anual=2.271)
    Cuantiabasica.objects.create(
        salario_inicio=4.2501, salario_fin=4.5,
        porcentaje_de_cuantia_basica=18.29,
        porcentaje_de_incremento_anual=2.302)
    Cuantiabasica.objects.create(
        salario_inicio=4.5001, salario_fin=4.75,
        porcentaje_de_cuantia_basica=17.3,
        porcentaje_de_incremento_anual=2.33)
    Cuantiabasica.objects.create(
        salario_inicio=4.7501, salario_fin=5,
        porcentaje_de_cuantia_basica=16.41,
        porcentaje_de_incremento_anual=2.355)
    Cuantiabasica.objects.create(
        salario_inicio=5.0001, salario_fin=5.25,
        porcentaje_de_cuantia_basica=15.61,
        porcentaje_de_incremento_anual=2.377)
    Cuantiabasica.objects.create(
        salario_inicio=5.2501, salario_fin=5.5,
        porcentaje_de_cuantia_basica=14.88,
        porcentaje_de_incremento_anual=2.398)
    Cuantiabasica.objects.create(
        salario_inicio=5.5001, salario_fin=5.75,
        porcentaje_de_cuantia_basica=14.22,
        porcentaje_de_incremento_anual=2.416)
    Cuantiabasica.objects.create(
        salario_inicio=5.7501, salario_fin=6,
        porcentaje_de_cuantia_basica=13.62,
        porcentaje_de_incremento_anual=2.433)
    Cuantiabasica.objects.create(
        salario_inicio=6.0001, salario_fin=99.9999,
        porcentaje_de_cuantia_basica=13,
        porcentaje_de_incremento_anual=2.45)

    Factoredad.objects.all().delete()
    Factoredad.objects.create(edad=60, factor_de_edad=75)
    Factoredad.objects.create(edad=61, factor_de_edad=80)
    Factoredad.objects.create(edad=62, factor_de_edad=85)
    Factoredad.objects.create(edad=63, factor_de_edad=90)
    Factoredad.objects.create(edad=64, factor_de_edad=95)
    Factoredad.objects.create(edad=65, factor_de_edad=100)


def upd190624():
    for r in HistoriaLaboralRegistro.objects.all():
        print("Procesando para {}".format(r))
        r.setDates()
