from django.db import models
from datetime import date

from routines.utils import BootstrapColors
from initsys.models import Usr, Direccion
from .models_opcs import *


def UsuarioCliente():
    return list(item['idusuario'] for item in Cliente.objects.all().values('idusuario'))

def UsuarioNoCliente():
    return list(item['idusuario'] for item in Usr.objects.exclude(idusuario__in=UsuarioCliente()).values('idusuario'))

def UsrResponsables():
    return [(item.pk, f"{item}") 
        for item in Usr.objects.filter(idusuario__in=UsuarioNoCliente())]


class TaxonomiaExpediente(models.Model):
    idtaxonomia = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    color = models.CharField(
        max_length=50, blank=True, choices=BootstrapColors,
        default=BootstrapColors[0][0])
    descripcion = models.TextField(
        blank=True, verbose_name="Descripción")
    mostrar_en_panel = models.BooleanField(default=False, blank=True)
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
    clinica = models.CharField(
        max_length=150, blank=True, verbose_name="Clínica")
    subdelegacion = models.CharField(
        max_length=150, blank=True, verbose_name="Subdelegación")
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
    obs_semanas_cotizadas = models.TextField(
        blank=True, verbose_name="Semanas Cotizadas")
    obs_homonimia = models.TextField(
        blank=True, verbose_name="Homonimia")
    obs_duplicidad = models.TextField(
        blank=True, verbose_name="Duplicidad")
    responsable = models.ForeignKey(
        Usr,
        on_delete=models.SET_NULL,
        related_name="clientes_asignados",
        blank=True,
        null=True,
        verbose_name="Ejecutivo",
        #limit_choices_to={'idusuario__in':UsuarioNoCliente}
        )
    gestor = models.ForeignKey(
        Usr,
        on_delete=models.SET_NULL,
        related_name="clientes_gestionados",
        blank=True,
        null=True,
        verbose_name="Gestor",
        #limit_choices_to={'idusuario__in':UsuarioNoCliente}
        )

    @property
    def edad(self):
        anios = date.today().year - self.fecha_nacimiento.year
        if date.today().month < self.fecha_nacimiento.month:
            anios -= 1
        elif (date.today().month == self.fecha_nacimiento.month
                and date.today().day < self.fecha_nacimiento.day):
            anios -= 1
        return anios

    class Meta:
        ordering = ["last_name", "apellido_materno", "first_name"]

    def __str__(self):
        return "{} {} {} - {}".format(
            self.last_name,
            self.apellido_materno,
            self.first_name,
            self.pk,
            ).strip()

    def __unicode__(self):
        return self.__str__()

