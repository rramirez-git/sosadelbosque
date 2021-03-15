from django.db import models
from django.db.models import Max, Min, Sum
from datetime import date, timedelta

import pandas as pd
import sys

from initsys.models import Usr, Direccion
from simple_tasks.models import Tarea
from routines.utils import BootstrapColors, inter_periods_days, free_days
from app.data_utils import (
    df_data_generate_HLRDDay, df_load_HLRDDay, df_load_HLRDDay_agg,
    df_save_HLRDDay,
    df_update,
    df_load_HLRD_periodo_continuo_laborado,
    df_generate_HLRD_periodo_continuo_laborado,
    df_generate_data_cotiz_HLRD_periodo_continuo_laborado,
    df_save_HLRD_periodo_continuo_laborado,
    delete_files,
    df_reset_data,
)

from .models_opcs import *
from .models_documentos import *
from .models_actividades import *
from .models_cliente import *
from .models_historialaboral import *


class AssocCteTarea(models.Model):
    idassocCteTarea = models.AutoField(primary_key=True)
    cte = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="tareas")
    tarea = models.ForeignKey(
        Tarea, on_delete=models.CASCADE, related_name="clientes")
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
            'cte',
            'tarea',
            'created_at',
        ]

    def __str__(self):
        return "{}-{}".format(self.cte, self.tarea)

    def __unicode__(self):
        return self.__str__()


class AssocActTarea(models.Model):
    idassocActTarea = models.AutoField(primary_key=True)
    actividad = models.ForeignKey(
        Actividad, on_delete=models.CASCADE, related_name="tareas")
    tarea = models.ForeignKey(
        Tarea, on_delete=models.CASCADE, related_name="actividades")
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
            'actividad',
            'tarea',
            'created_at',
        ]

    def __str__(self):
        return "{}-{}".format(self.actividad, self.tarea)

    def __unicode__(self):
        return self.__str__()


class AssocHistLabTarea(models.Model):
    idassocHistLabTarea = models.AutoField(primary_key=True)
    historial = models.ForeignKey(
        HistoriaLaboral, on_delete=models.CASCADE, related_name="tareas")
    tarea = models.ForeignKey(
        Tarea, on_delete=models.CASCADE, related_name="historiales")
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
            'historial',
            'tarea',
            'created_at',
        ]

    def __str__(self):
        return "{}-{}".format(self.historial, self.tarea)

    def __unicode__(self):
        return self.__str__()
