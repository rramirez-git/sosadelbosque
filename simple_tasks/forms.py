from django import forms
from django.contrib import auth

from .models import Tarea


class FrmTarea(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = [
            'titulo',
            'descripcion',
            'responsable',
            'fecha_limite',
            'estado_actual'
        ]
