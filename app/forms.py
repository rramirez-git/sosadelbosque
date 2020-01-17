from django import forms

from .models import (TaxonomiaExpediente, Cliente, DoctoGral,
                     TipoActividad, TipoDocumento, EstatusActividad,
                     Actividad, ActividadHistoria, Externo, UMA,
                     Cuantiabasica, Factoredad, UsrResponsables)

from initsys.models import Usr


class frmTaxonomia(forms.ModelForm):

    class Meta:
        model = TaxonomiaExpediente
        fields = [
            'nombre',
            'color',
            'mostrar_en_panel',
            'descripcion',
        ]


class frmCliente(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = [
            'usuario',
            'contraseña',
            'first_name',
            'last_name',
            'apellido_materno',
            'tipo',
            'email',
            'telefono',
            'celular',
            'telefono_oficina',
            'otro_telefono',
            'fotografia',
            'fecha_nacimiento',
            'CURP',
            'RFC',
            'NSS',
            'estado_civil',
            'conyuge',
            'empresa',
            'afore_actual',
            'fecha_afore_actual',
            'clinica',
            'subdelegacion',
            'observaciones',
            'obs_semanas_cotizadas',
            'obs_homonimia',
            'obs_duplicidad',
            'responsable'
        ]
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido Paterno',
            'email': 'E-Mail',
            'tipo': 'Tipo de Expediente',
        }
        widgets = {
            'telefono': forms.TextInput(attrs={'type': 'tel'}),
            'celular': forms.TextInput(attrs={'type': 'tel'}),
            'telefono_oficina': forms.TextInput(attrs={'type': 'tel'}),
            'otro_telefono': forms.TextInput(attrs={'type': 'tel'}),
            'fecha_nacimiento': forms.TextInput(attrs={'type': 'date'}),
            'fecha_afore_actual': forms.TextInput(attrs={'type': 'date'}),
        }


class frmClienteUsuario(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = [
            'usuario',
            'contraseña',
            'first_name',
            'last_name',
            'apellido_materno',
            'tipo',
            'fotografia',
            'fecha_nacimiento',
            'CURP',
            'RFC',
            'NSS',
            'estado_civil',
            'conyuge',
            'empresa',
            'afore_actual',
            'fecha_afore_actual',
            'clinica',
            'subdelegacion',
        ]
        widgets = {
            'fecha_nacimiento': forms.TextInput(attrs={'type': 'date'}),
            'fecha_afore_actual': forms.TextInput(attrs={'type': 'date'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido Paterno',
            'tipo': 'Tipo de Expediente',
        }


class frmClienteContacto(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = [
            'email',
            'telefono',
            'celular',
            'telefono_oficina',
            'otro_telefono',
        ]
        labels = {
            'email': 'E-Mail',
        }
        widgets = {
            'telefono': forms.TextInput(attrs={'type': 'tel'}),
            'celular': forms.TextInput(attrs={'type': 'tel'}),
            'telefono_oficina': forms.TextInput(attrs={'type': 'tel'}),
            'otro_telefono': forms.TextInput(attrs={'type': 'tel'}),
        }


class frmClienteObservaciones(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ['observaciones']

class frmClienteObservacionesExtra(forms.ModelForm):
    responsable = forms.ChoiceField(required=False, choices=UsrResponsables)

    class Meta:
        model = Cliente
        fields = [
            'obs_semanas_cotizadas',
            'obs_homonimia',
            'obs_duplicidad',
        ]


class frmDocument(forms.ModelForm):

    class Meta:
        model = DoctoGral
        fields = [
            'tipo_de_documento',
            'anverso',
            'observaciones'
        ]
        labels = {
            'anverso': 'Archivo',
        }


class frmTipoActividad(forms.ModelForm):

    class Meta:
        model = TipoActividad
        fields = [
            'nombre',
        ]


class frmEstatusActividad(forms.ModelForm):

    class Meta:
        model = EstatusActividad
        fields = [
            'nombre',
            'color',
            'mostrar_en_panel',
        ]


class frmTipoDocumento(forms.ModelForm):

    class Meta:
        model = TipoDocumento
        fields = [
            'nombre',
            'visible_para_usuario'
        ]


class frmActividad(forms.ModelForm):

    class Meta:
        model = Actividad
        fields = [
            'tipo_de_actividad',
            'titulo',
            'estado',
            'responsable',
            'comentarios',
        ]


class frmActividadUpd(forms.ModelForm):

    class Meta:
        model = Actividad
        fields = [
            'tipo_de_actividad',
            'titulo',
            'responsable',
            'comentarios',
        ]


class frmActividadHistoria(forms.ModelForm):

    class Meta:
        model = ActividadHistoria
        fields = [
            'estado_nuevo',
            'observaciones'
        ]


class frmExterno(forms.ModelForm):

    class Meta:
        model = Externo
        fields = [
            'nombre',
            'apellido_paterno',
            'apellido_materno'
        ]


class frmUMA(forms.ModelForm):

    class Meta:
        model = UMA
        fields = [
            'año',
            'valor'
        ]


class frmCuantiaBasica(forms.ModelForm):

    class Meta:
        model = Cuantiabasica
        fields = [
            'salario_inicio',
            'salario_fin',
            'porcentaje_de_cuantia_basica',
            'porcentaje_de_incremento_anual',
        ]


class frmFactorEdad(forms.ModelForm):

    class Meta:
        model = Factoredad
        fields = [
            'edad',
            'factor_de_edad',
        ]
