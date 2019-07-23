from django.db import models
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group

from datetime import date

from routines.utils import print_error, clean_name
from routines.logger import Logger

# Create your models here.

usr_upload_to = 'usuarios'
setting_upload_to = "settings"


class Permiso(Permission):
    """
    Permiso para estructura de perfiles.

    Hereda de django.contrib.auth.models.Permission.
    """
    idpermiso = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    mostrar_como = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    vista = models.CharField(max_length=100, blank=True)
    permiso_padre = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='+',
        null=True, blank=True)
    es_operacion = models.BooleanField(default=False)
    posicion = models.PositiveSmallIntegerField(default=0)
    created_by = models.ForeignKey(
        'Usr', on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        'Usr', on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['posicion', 'nombre']

    def __unicode__(self):
        """
        Definicion genérica de conversion a string.
        """
        if self.nombre.strip().lower() == self.mostrar_como.strip().lower():
            return self.nombre
        return "{} ({})".format(self.nombre, self.mostrar_como)

    def __str__(self):
        """
        Definicion genérica de conversion a string.
        """
        return self.__unicode__()

    def hijos(self):
        """
        Obtiene los hijos del Permiso.

        return list de Permiso
        """
        return list(Permiso.objects.filter(permiso_padre__pk=self.pk))

    def descendencia(self):
        """
        Genera el árbol recursivo de decsendencia a partir del permiso.

        return list de Permiso con los hijos directos y su árbol de
            descendencia
        """
        desc = []
        for hijo in self.hijos():
            desc.append(hijo)
            for nieto in hijo.descendencia():
                desc.append(nieto)
        return desc

    def depth(self):
        """
        Obtiene el nivel de profundidad del permiso.

        return integer
        """
        if self.permiso_padre is None:
            return 0
        else:
            return self.permiso_padre.depth() + 1

    def depth_name(self, fill_with='&nbsp;&nbsp;&nbsp;&nbsp;'):
        """
        Devuelve el nombre del objeto con cadena de profundidad.

        (string) fill_with = '&nbsp;&nbsp;&nbsp;&nbsp;' Cadena de relleno
                                                        de nivel de
                                                        profundidad.
        """
        return "{}{}".format(fill_with * self.depth(), self)

    def perm(self):
        """
        Devuelve el permission base del permiso.

        return Permission
        """
        return super(Permiso, self)

    @staticmethod
    def get_from_perms(model, codename):
        """
        Obtiene un Permiso con base en el modelo y el codename del permiso

        (string) model      modelo al que corresponde el permiso
        (string) codename   codename generado para el permiso

        return None | Permiso
        """
        perm = Permission.objects.filter(
            content_type__model=model, codename=codename)
        if 0 == perm.count():
            return None
        permiso = Permiso.objects.filter(id=perm[0].pk)
        if 0 == permiso.count():
            return None
        return permiso[0]

    @staticmethod
    def create(
            name,
            app_label,
            model,
            posicion,
            mostrar_como=None,
            vista='',
            es_operacion=False,
            permiso_padre=None,
            groups=[]):
        ct = ContentType.objects.get(app_label=app_label, model=model)
        if mostrar_como is None:
            mostrar_como = name

        perm = Permiso.objects.create(
            nombre=name,
            name=name,
            codename="{}_{}".format(clean_name(name), ct),
            mostrar_como=mostrar_como,
            vista=vista,
            es_operacion=es_operacion,
            posicion=posicion,
            permiso_padre=permiso_padre,
            content_type=ct
        )
        for g in groups:
            if Group.objects.filter(name=g).exists():
                gpo = Group.objects.get(name=g)
                gpo.permissions.add(perm)
                gpo.save()
        return perm

    @staticmethod
    def get_from_package_codename(model_codename):
        """
        Obtiene un Permiso con base en el formato "model.codename".

        (string) model_codename cadena en formato modelo.codename

        return None | Permiso
        """
        elems = model_codename.split('.')
        return Permiso.get_from_perms(elems[0], elems[1])


class Usr(User):
    """
    Estructura de Usr con campos personalizados

    Hereda de django.contrib.auth.models.User.
    """
    idusuario = models.AutoField(primary_key=True)
    usuario = models.CharField(unique=True, max_length=50)
    contraseña = models.CharField(max_length=250)
    apellido_materno = models.CharField(
        blank=True,
        max_length=200,
        verbose_name="Apellido Materno")
    telefono = models.CharField(max_length=10, blank=True)
    celular = models.CharField(max_length=10, blank=True)
    fotografia = models.ImageField(
        blank=True, upload_to=usr_upload_to, verbose_name='Fotografía')
    depende_de = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='+',
        null=True, blank=True)
    created_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        """
        Definicion genérica de conversion a string.
        """
        return self.get_full_name()

    def __str__(self):
        """
        Definicion genérica de conversion a string.
        """
        return self.get_full_name()

    def __gt__(self, usr2):
        """
        Definicion genérica de operador >.
        """
        return self.__str__() > usr2.__str__()

    def __ge__(self, usr2):
        """
        Definicion genérica de operador >=.
        """
        return self.__str__() >= usr2.__str__()

    def __lt__(self, usr2):
        """
        Definicion genérica de operador <.
        """
        return self.__str__() < usr2.__str__()

    def __le__(self, usr2):
        """
        Definicion genérica de operador <=.
        """
        return self.__str__() <= usr2.__str__()

    def hijos(self):
        """
        Obtiene los hijos dependientes del Usr.

        return list de Usr
        """
        return list(Usr.objects.filter(depende_de=self))

    def depth(self):
        """
        Obtiene el nivel de profundidad del usuario.

        return integer
        """
        if self.depende_de is None:
            return 0
        return self.depende_de.depth() + 1

    def depth_name(self, fill_with='&nbsp;&nbsp;&nbsp;&nbsp;'):
        """
        Devuelve el nombre del objeto con cadena de profundidad.

        (string) fill_with = '&nbsp;&nbsp;&nbsp;&nbsp;' Cadena de relleno
                                                        de nivel de
                                                        profundidad.
        """
        return "{}{}".format(fill_with * self.depth(), self)

    def descendencia(self):
        """
        Genera el árbol recursivo de decsendencia a partir del uaurio.

        return list de Usr con los hijos directos y su árbol de
            descendencia
        """
        desc = []
        for hijo in self.hijos():
            desc.append(hijo)
            for nieto in hijo.descendencia():
                desc.append(nieto)
        return desc

    def has_perm_or_has_perm_child(self, model_codename):
        """
        Determina si el usuario tiene un permiso establecido

        (string) model_codename cadena en formato modelo.codename

        return boolean
        """
        perms = []
        permiso = Permiso.get_from_package_codename(model_codename)
        if permiso is None:
            Logger.write("No se encontró el permiso: " + model_codename)
            return False
        perms.append(permiso.perm())
        desc = permiso.descendencia()
        for p in desc:
            perms.append(p.perm())
        return_value = False
        for perm in perms:
            p = "{}.{}".format(perm.content_type.app_label, perm.codename)
            if super(Usr, self).has_perm(p):
                return_value = True
        return return_value

    def main_menu_struct(self):
        """
        Genera la estructura de árbol de dos niveles con permisos del
        usuario.

        return dict {'perms':items}
            items es list de {
                'permiso': Permiso raiz,
                'items': lista de Permisos descendencia de permiso raiz,
                'items_qyt': cantidad de elementos
                }
        """
        mm = []
        root_perms = Permiso.objects.filter(permiso_padre__isnull=True)
        for rp in root_perms:
            if self.has_perm_or_has_perm_child(
                    "{}.{}".format(rp.content_type.model, rp.codename)):
                items = []
                for p in rp.descendencia():
                    if ((p.es_operacion is False) and
                            self.has_perm_or_has_perm_child(
                                "{}.{}".format(
                                    p.content_type.model, p.codename))):
                        items.append(p)
                item = {
                    'permiso': rp,
                    'items': items,
                    'items_qty': len(items)
                }
                mm.append(item)
        return {'perms': mm}

    def is_admin(self):
        """
        Determina si el Usr es administrador.

        Se basa en que el usuario sea superusuario o tenga asignado un
        perfil que contenga Administrador o Super-Administrador

        return boolean
        """
        return (self.is_superuser or
                self.groups.filter(
                    name__icontains="Administrador").exists() or
                self.groups.filter(
                    name__icontains="Super-Administrador").exists())

    class Meta:
        ordering = ['first_name', 'last_name', 'apellido_materno']


class Setting(models.Model):
    ENTERO = 'INTEGER'
    CADENA = 'STRING'
    TEXTO_LARGO = 'TEXT'
    IMAGEN = 'PICTURE'
    ARCHIVO = 'FILE'
    TIPOS_SETTING = (
        (ENTERO, 'Entero'),
        (CADENA, 'Cadena'),
        (TEXTO_LARGO, 'Texto Largo'),
        (IMAGEN, 'Imagen'),
        (ARCHIVO, 'Archivo'),
    )
    idsetting = models.AutoField(primary_key=True)
    seccion = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    nombre_para_mostrar = models.CharField(max_length=100)
    valor = models.TextField()
    tipo = models.CharField(
        max_length=20, choices=TIPOS_SETTING, default=CADENA)
    es_multiple = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['seccion', 'nombre_para_mostrar']

    def __unicode__(self):
        return "{}: {}".format(self.nombre_para_mostrar, self.valor)

    def __str__(self):
        return self.__unicode__()

    @staticmethod
    def get_value(seccion, nombre):
        """
        Obtiene el valor de un setting

        (string) section    Seccion del setting
        (string) nombre     Nombre del setting

        return string
        """
        obj = Setting.objects.filter(seccion=seccion, nombre=nombre)
        if obj.exists():
            return obj[0].valor
        return ""


class Direccion(models.Model):
    iddireccion = models.AutoField(primary_key=True)
    calle = models.CharField(max_length=100, blank=True)
    numero_exterior = models.CharField(
        max_length=10,
        verbose_name="No. Exterior",
        blank=True)
    numero_interior = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="No. Interior")
    codigo_postal = models.CharField(max_length=5, blank=True)
    colonia = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(
        max_length=100,
        verbose_name="Alcaldía o Municipio",
        blank=True)
    estado = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.numero_interior:
            return "{} {} (Int. {}), {}, {}, {}, C.P. {}".format(
                self.calle, self.numero_exterior, self.numero_interior,
                self.colonia, self.municipio, self.estado,
                self.codigo_postal)
        else:
            return "{} {}, {}, {}, {}, C.P. {}".format(
                self.calle, self.numero_exterior, self.colonia,
                self.municipio, self.estado, self.codigo_postal)

    def __unicode__(self):
        return self.__str__()

    def asDireccion(self):
        if self.numero_interior:
            return (
                "{} {} (Int. {}),<br />{}, {},<br />{},<br />"
                "C.P. {}").format(
                    self.calle, self.numero_exterior, self.numero_interior,
                    self.colonia, self.municipio, self.estado,
                    self.codigo_postal)
        else:
            return "{} {},<br />{}, {},<br />{},<br />C.P. {}".format(
                self.calle, self.numero_exterior, self.colonia,
                self.municipio, self.estado, self.codigo_postal)


class Nota(models.Model):
    usuario = models.ForeignKey(
        Usr, on_delete=models.CASCADE, related_name="notas")
    nota = models.TextField()
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return "{}".format(self.nota)

    def __unicode__(self):
        return self.__str__()


class Alerta(models.Model):
    usuario = models.ForeignKey(
        Usr, on_delete=models.CASCADE, related_name="alertas")
    nota = models.TextField()
    fecha_alerta = models.DateField()
    alertado = models.BooleanField(default=False)
    fecha_alertado = models.DateField(null=True, blank=True)
    mostrar_alerta = models.BooleanField(default=True)
    fecha_no_mostrar = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            '-fecha_alerta',
            '-created_at',
            'alertado',
            'mostrar_alerta']

    def __str__(self):
        return "{}: {}".format(self.fecha_alerta, self.nota)

    def __unicode__(self):
        return self.__str__()
