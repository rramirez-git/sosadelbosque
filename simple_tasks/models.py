from django.db import models
from django.contrib.auth.models import User

from datetime import date, timedelta

# Create your models here.

STATUS_TAREA = (
    ('PENDIENTE', 'PENDIENTE'),
    ('EN PROGRESO', 'EN PROGRESO'),
    ('EN REVISION', 'EN REVISION'),
    ('REALIZADO', 'REALIZADO'),
    ('CANCELADO', 'CANCELADO'),
    ('OTRO', 'OTRO'),
)

class Tarea(models.Model):
    idtarea = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=250)
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    responsable = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='tareas_asignadas',
        null=True, blank=True)
    fecha_limite = models.DateField(
        default=date.today, verbose_name="Fecha límite")
    estado_actual = models.CharField(
        max_length=50, choices=STATUS_TAREA, verbose_name="Status")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True, verbose_name="Creado por")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación")
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True, verbose_name="Actualizado por")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = [
            'fecha_limite',
            'titulo',
        ]

    def __str__(self):
        return "{:03d}-{}".format(self.idtarea, self.titulo)

    def __unicode__(self):
        return self.__str__()

    @property
    def color(self):
        if "REALIZADO" == self.estado_actual:
            return "success"
        elif "CANCELADO" == self.estado_actual:
            return "light"
        elif "OTRO" == self.estado_actual:
            return "light"
        elif "EN REVISION" == self.estado_actual:
            return "secondary"
        else:
            if date.today() > self.fecha_limite:
                return "danger"
            if date.today() + timedelta(3) > self.fecha_limite:
                return "warning"
        return "primary"

class Vinculo(models.Model):
    idvinculo = models.AutoField(primary_key=True)
    tarea = models.ForeignKey(
        Tarea, on_delete=models.CASCADE, related_name='vinclulos')
    tipo = models.CharField(max_length=100)
    texto = models.CharField(max_length=150)
    url = models.URLField(max_length=250)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = [
            'tarea',
            'tipo',
            'texto',
        ]

    def __str__(self):
        return '{}: <a href="{}" target="_blank">{}</a>'.format(
            self.tipo, self.url, self.texto)

    def __unicode__(self):
        return self.__str__()

class Historia(models.Model):
    idhistoria = models.AutoField(primary_key=True)
    tarea = models.ForeignKey(
        Tarea, on_delete=models.CASCADE, related_name='historia')
    cambio = models.CharField(max_length=250)
    valor_anterior = models.TextField(blank=True)
    valor_nuevo = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = [
            'tarea',
            'created_at',
            'idhistoria',
        ]

    def __str__(self):
        return "{}".format(self.cambio)

    def __unicode__(self):
        return self.__str__()

class Comentario(models.Model):
    idcomentario = models.AutoField(primary_key=True)
    tarea = models.ForeignKey(
        Tarea, on_delete=models.CASCADE, related_name='comentarios')
    comentario = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='+',
        null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = [
            'tarea',
            'created_at',
            'idcomentario',
        ]

    def __str__(self):
        return "{}".format(self.comentario)

    def __unicode__(self):
        return self.__str__()
