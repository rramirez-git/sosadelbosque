from django.db import models

from .models_cliente import *


def docto_upload_to(instance, filename):
    return 'documentos/usr_{0}/{1}'.format(instance.cliente.pk, filename)


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
    tipo_de_documento = models.ForeignKey(
        to='TipoDocumento',
        on_delete=models.PROTECT,
        related_name='documentos')
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tipo_de_documento", "iddoctogral"]

    def __str__(self):
        res = "{}".format(self.tipo_de_documento)
        return res

    def __unicode__(self):
        return self.__str__()


class TipoDocumento(models.Model):
    idtipodocumento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    visible_para_usuario = models.BooleanField(default=True)
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
