from django.db import models
from datetime import date

from initsys.models import Usr, Direccion

# Create your models here.

def docto_upload_to(instance, filename):
    return 'documentos/usr_{0}/{1}'.format(instance.cliente.pk, filename)


ESTADO_CIVIL_SOLTERO = "Soltero"
ESTADO_CIVIL_CASADO = "Casado"
ESTADO_CIVIL_UNION_LIBRE = "UnionLibre"
ESTADO_CIVIL_SEPARADO = "Separado"
ESTADO_CIVIL_DIVORCIADO = "Divorciado"
ESTADO_CIVIL_VIUDO = "Viudo"
ESTADOS_CIVILES = (
    (ESTADO_CIVIL_CASADO, "Casado"),
    (ESTADO_CIVIL_DIVORCIADO, "Divorciado"),
    (ESTADO_CIVIL_SEPARADO, "Separado"),
    (ESTADO_CIVIL_SOLTERO, "Soltero"),
    (ESTADO_CIVIL_UNION_LIBRE, "Unión Libre"),
    (ESTADO_CIVIL_VIUDO, "Viudo"),
)


TIPO_DOCUMENTO_GRAL_ACTA_DE_NACIMIENTO = 'Acta de Nacimiento'
TIPO_DOCUMENTO_GRAL_CURP = 'CURP'
TIPO_DOCUMENTO_GRAL_INE = 'INE'
TIPO_DOCUMENTO_GRAL_RFC = 'RFC'
TIPO_DOCUMENTO_GRAL_IMSS = 'IMSS'
TIPO_DOCUMENTO_GRAL_ESTADO_DE_CUENTA_AFORE = 'Estado de Cuenta Afore'
TIPO_DOCUMENTO_GRAL_CARTA_A_DIRECCION_DE_PRESTACIONES_ECONOMICAS = 'Carta a Dirección de Prestaciones Económicas'
TIPO_DOCUMENTO_GRAL_CARTA_DE_INSCRIPCION_MOD40 = 'Carta de Inscripción MOD40'
TIPO_DOCUMENTO_GRAL_CARTA_DE_AFORE = 'Carta de AFORE'
TIPO_DOCUMENTO_GRAL_CLAVE_DE_ACCESO_A_SISTEMA_REPORTE_SEMANAS_COTIZADAS = 'Clave de Acceso a Sistema de Reporte de Semanas Cotizadas'
TIPO_DOCUMENTO_GRAL_CORRECCION_EN_PROCESAR = 'Corrección en Procesar'
TIPO_DOCUMENTO_GRAL_CORRECCION_EN_IMSS = 'Corrección en IMSS'
TIPO_DOCUMENTO_GRAL_REPORTE_DE_SEMANAS_COTIZADAS = 'Reporte de Semanas Cotizadas'
TIPOS_DOCUMENTO_GRAL = (
    (TIPO_DOCUMENTO_GRAL_ACTA_DE_NACIMIENTO, TIPO_DOCUMENTO_GRAL_ACTA_DE_NACIMIENTO),
    (TIPO_DOCUMENTO_GRAL_CARTA_A_DIRECCION_DE_PRESTACIONES_ECONOMICAS, TIPO_DOCUMENTO_GRAL_CARTA_A_DIRECCION_DE_PRESTACIONES_ECONOMICAS),
    (TIPO_DOCUMENTO_GRAL_CARTA_DE_AFORE, TIPO_DOCUMENTO_GRAL_CARTA_DE_AFORE),
    (TIPO_DOCUMENTO_GRAL_CARTA_DE_INSCRIPCION_MOD40, TIPO_DOCUMENTO_GRAL_CARTA_DE_INSCRIPCION_MOD40),
    (TIPO_DOCUMENTO_GRAL_CLAVE_DE_ACCESO_A_SISTEMA_REPORTE_SEMANAS_COTIZADAS, TIPO_DOCUMENTO_GRAL_CLAVE_DE_ACCESO_A_SISTEMA_REPORTE_SEMANAS_COTIZADAS),
    (TIPO_DOCUMENTO_GRAL_CORRECCION_EN_IMSS, TIPO_DOCUMENTO_GRAL_CORRECCION_EN_IMSS),
    (TIPO_DOCUMENTO_GRAL_CORRECCION_EN_PROCESAR, TIPO_DOCUMENTO_GRAL_CORRECCION_EN_PROCESAR),
    (TIPO_DOCUMENTO_GRAL_CURP, TIPO_DOCUMENTO_GRAL_CURP),
    (TIPO_DOCUMENTO_GRAL_ESTADO_DE_CUENTA_AFORE, TIPO_DOCUMENTO_GRAL_ESTADO_DE_CUENTA_AFORE),
    (TIPO_DOCUMENTO_GRAL_IMSS, TIPO_DOCUMENTO_GRAL_IMSS),
    (TIPO_DOCUMENTO_GRAL_INE, TIPO_DOCUMENTO_GRAL_INE),
    (TIPO_DOCUMENTO_GRAL_REPORTE_DE_SEMANAS_COTIZADAS, TIPO_DOCUMENTO_GRAL_REPORTE_DE_SEMANAS_COTIZADAS),
    (TIPO_DOCUMENTO_GRAL_RFC, TIPO_DOCUMENTO_GRAL_RFC),
)


class TaxonomiaExpediente(models.Model):
    idtaxonomia = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(
        blank=True, verbose_name="Descripción")
    padre = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="hijos")
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return "{}".format(self.nombre).strip()

    def __unicode__(self):
        return self.__str__()


class Cliente(Usr):
    idcliente = models.AutoField(primary_key=True)
    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de nacimiento", blank=True, default=date.today)
    CURP = models.CharField(max_length=18, blank=True)
    RFC = models.CharField(max_length=13, blank=True)
    NSS = models.CharField(max_length=15, blank=True)
    estado_civil = models.CharField(
        max_length=15,
        choices=ESTADOS_CIVILES,
        default=ESTADO_CIVIL_CASADO)
    conyuge = models.CharField(max_length=150, blank=True)
    clinica = models.CharField(max_length=150, blank=True, verbose_name="Clínica")
    subdelegacion = models.CharField(max_length=150, blank=True, verbose_name="Subdelegación")
    empresa = models.CharField(max_length=150, blank=True)
    domicilicio = models.ForeignKey(
        Direccion, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="cliente")
    telefono_oficina = models.CharField(
        max_length=10, blank=True, verbose_name="Teléfono de oficina")
    otro_telefono = models.CharField(
        max_length=10, blank=True, verbose_name="Otro teléfono")
    afore_actual = models.CharField(max_length=50, blank=True)
    fecha_afore_actual = models.DateField(blank=True, default=date.today)
    tipo = models.ForeignKey(
        TaxonomiaExpediente,
        on_delete=models.PROTECT,
        related_name='clientes')
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ["first_name", "last_name", "apellido_materno"]

    def __str__(self):
        return "{} {} {}".format(
            self.first_name,
            self.last_name,
            self.apellido_materno
            ).strip()

    def __unicode__(self):
        return self.__str__()

class DoctoGral(models.Model):
    iddoctogral = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, models.CASCADE, 'documentos')
    tipo = models.CharField(
        max_length=100,
        choices=TIPOS_DOCUMENTO_GRAL,
        default=TIPO_DOCUMENTO_GRAL_ACTA_DE_NACIMIENTO)
    mimetype_anverso = models.CharField(max_length=50)
    anverso = models.FileField(upload_to=docto_upload_to)
    mimetype_reverso = models.CharField(max_length=50, blank=True)
    reverso = models.FileField(upload_to=docto_upload_to, blank=True)
    observaciones = models.TextField(blank=True)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tipo", "iddoctogral"]

    def __str__(self):
        res = "{}".format(self.tipo)
        return res

    def __unicode__(self):
        return self.__str__()

