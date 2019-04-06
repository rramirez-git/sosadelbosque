from django.db import models

from initsys.models import Usr, Direccion

# Create your models here.

ESTADO_CIVIL_SOLTERO = "Soltero"
ESTADO_CIVIL_CASADO = "Casado"
ESTADO_CIVIL_UNION_LIBRE = "UnionLibre"
ESTADO_CIVIL_SEPARADO = "Separado"
ESTADO_CIVIL_DIVORCIADO = "Divorciado"
ESTADO_CIVIL_VIUDO = "Viudo"
ESTADOS_CVILES = (
    (ESTADO_CIVIL_CASADO, "Casado"),
    (ESTADO_CIVIL_DIVORCIADO, "Divorciado"),
    (ESTADO_CIVIL_SEPARADO, "Separado"),
    (ESTADO_CIVIL_SOLTERO, "Soltero"),
    (ESTADO_CIVIL_UNION_LIBRE, "Unión Libre"),
    (ESTADO_CIVIL_VIUDO, "Viudo"),
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
    fecha_nacimiento = models.DateField(verbose_name="Fecha de nacimiento")
    CURP = models.CharField(max_length=18)
    RFC = models.CharField(max_length=13)
    NSS = models.CharField(max_length=15)
    estado_civil = models.CharField(
        max_length=15,
        choices=ESTADOS_CVILES,
        default=ESTADO_CIVIL_CASADO)
    empresa = models.CharField(max_length=150)
    domicilicio = models.ForeignKey(
        Direccion, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="cliente")
    telefono_oficina = models.CharField(
        max_length=10, blank=True, verbose_name="Teléfono de oficina")
    otro_telefono = models.CharField(
        max_length=10, blank=True, verbose_name="Otro teléfono")
    afore_actual = models.CharField(max_length=50)
    fecha_afore_actual = models.DateField(blank=True)
    tipo = models.ForeignKey(
        TaxonomiaExpediente,
        on_delete=models.PROTECT,
        related_name='clientes')

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
