from django.db import models

from routines.utils import BootstrapColors
from initsys.models import Usr
from .models_cliente import *


class EstatusActividad(models.Model):
    idestatusactividad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    color = models.CharField(
        max_length=50, blank=True, choices=BootstrapColors,
        default=BootstrapColors[0][0])
    mostrar_en_panel = models.BooleanField(default=False, blank=True)
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
        res = "{}".format(self.nombre)
        return res

    def __unicode__(self):
        return self.__str__()


class TipoActividad(models.Model):
    idtipoactividad = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
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
        res = "{}".format(self.nombre)
        return res

    def __unicode__(self):
        return self.__str__()


class MedioActividad(models.Model):
    idmedioctividad = models.AutoField(primary_key=True)
    medio = models.CharField(max_length=50)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["medio"]

    def __str__(self):
        res = "{}".format(self.medio)
        return res

    def __unicode__(self):
        return self.__str__()


class Externo(models.Model):
    idexterno = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100, blank=True)
    apellido_materno = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre", 'apellido_paterno', 'apellido_materno']

    def __str__(self):
        res = "{} {} {}".format(
            self.nombre, self.apellido_paterno,
            self.apellido_materno)
        return res.strip()

    def __unicode__(self):
        return self.__str__()


class Actividad(models.Model):
    idactividad = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=150)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE,
        related_name='actividades_asociadas')
    tipo_de_actividad = models.ForeignKey(
        TipoActividad, on_delete=models.PROTECT,
        related_name='actividades_de_tipo')
    estado = models.ForeignKey(
        EstatusActividad, on_delete=models.PROTECT,
        related_name='actividades')
    comentarios = models.TextField(blank=True)
    responsable = models.ForeignKey(
        Externo, on_delete=models.PROTECT,
        related_name='resp_actividades')
    fecha = models.DateField(blank=True, null=True)
    medio = models.ForeignKey(
        MedioActividad, on_delete=models.PROTECT,
        related_name='actividades_con_medio')
    fecha_liquidado = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["estado", "-updated_at", "cliente"]

    def __str__(self):
        return "{}".format(self.titulo)

    def __unicode__(self):
        return self.__str__()


class ActividadHistoria(models.Model):
    idactividadhistoria = models.AutoField(primary_key=True)
    actividad = models.ForeignKey(
        Actividad, on_delete=models.CASCADE,
        related_name='detalle')
    observaciones = models.TextField(blank=True)
    estado_anterior = models.ForeignKey(
        EstatusActividad, on_delete=models.PROTECT,
        related_name='+')
    estado_nuevo = models.ForeignKey(
        EstatusActividad, on_delete=models.PROTECT,
        related_name='+')
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return "{} de {} a {}".format(
            self.actividad, self.estado_anterior, self.estado_nuevo)

    def __unicode__(self):
        return self.__str__()
