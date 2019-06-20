from django.db import models
from django.db.models import Max, Min, Sum
from datetime import date

import pandas as pd

from initsys.models import Usr, Direccion
from routines.utils import BootstrapColors

# Create your models here.


def docto_upload_to(instance, filename):
    return 'documentos/usr_{0}/{1}'.format(instance.cliente.pk, filename)


def getyear():
    return date.today().year


def getmaxUMA():
    try:
        return UMA.objects.all()[0].pk
    except IndexError:
        return 0


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
TIPO_DOCUMENTO_GRAL_CARTA_A_DIRECCION_DE_PRESTACIONES_ECONOMICAS = \
    'Carta a Dirección de Prestaciones Económicas'
TIPO_DOCUMENTO_GRAL_CARTA_DE_INSCRIPCION_MOD40 = \
    'Carta de Inscripción MOD40'
TIPO_DOCUMENTO_GRAL_CARTA_DE_AFORE = 'Carta de AFORE'
TIPO_DOCUMENTO_GRAL_CLAVE_DE_ACCESO_A_SISTEMA_REPORTE_SEMANAS_COTIZADAS = \
    'Clave de Acceso a Sistema de Reporte de Semanas Cotizadas'
TIPO_DOCUMENTO_GRAL_CORRECCION_EN_PROCESAR = 'Corrección en Procesar'
TIPO_DOCUMENTO_GRAL_CORRECCION_EN_IMSS = 'Corrección en IMSS'
TIPO_DOCUMENTO_GRAL_REPORTE_DE_SEMANAS_COTIZADAS = \
    'Reporte de Semanas Cotizadas'
TIPOS_DOCUMENTO_GRAL = (
  (
    TIPO_DOCUMENTO_GRAL_ACTA_DE_NACIMIENTO,
    TIPO_DOCUMENTO_GRAL_ACTA_DE_NACIMIENTO
  ),
  (
    TIPO_DOCUMENTO_GRAL_CARTA_A_DIRECCION_DE_PRESTACIONES_ECONOMICAS,
    TIPO_DOCUMENTO_GRAL_CARTA_A_DIRECCION_DE_PRESTACIONES_ECONOMICAS
  ),
  (
    TIPO_DOCUMENTO_GRAL_CARTA_DE_AFORE,
    TIPO_DOCUMENTO_GRAL_CARTA_DE_AFORE
  ),
  (
    TIPO_DOCUMENTO_GRAL_CARTA_DE_INSCRIPCION_MOD40,
    TIPO_DOCUMENTO_GRAL_CARTA_DE_INSCRIPCION_MOD40
  ),
  (
    TIPO_DOCUMENTO_GRAL_CLAVE_DE_ACCESO_A_SISTEMA_REPORTE_SEMANAS_COTIZADAS,
    TIPO_DOCUMENTO_GRAL_CLAVE_DE_ACCESO_A_SISTEMA_REPORTE_SEMANAS_COTIZADAS
  ),
  (
    TIPO_DOCUMENTO_GRAL_CORRECCION_EN_IMSS,
    TIPO_DOCUMENTO_GRAL_CORRECCION_EN_IMSS
  ),
  (
    TIPO_DOCUMENTO_GRAL_CORRECCION_EN_PROCESAR,
    TIPO_DOCUMENTO_GRAL_CORRECCION_EN_PROCESAR
  ),
  (
    TIPO_DOCUMENTO_GRAL_CURP,
    TIPO_DOCUMENTO_GRAL_CURP
  ),
  (
    TIPO_DOCUMENTO_GRAL_ESTADO_DE_CUENTA_AFORE,
    TIPO_DOCUMENTO_GRAL_ESTADO_DE_CUENTA_AFORE
  ),
  (
    TIPO_DOCUMENTO_GRAL_IMSS,
    TIPO_DOCUMENTO_GRAL_IMSS
  ),
  (
    TIPO_DOCUMENTO_GRAL_INE,
    TIPO_DOCUMENTO_GRAL_INE
  ),
  (
    TIPO_DOCUMENTO_GRAL_REPORTE_DE_SEMANAS_COTIZADAS,
    TIPO_DOCUMENTO_GRAL_REPORTE_DE_SEMANAS_COTIZADAS
  ),
  (
    TIPO_DOCUMENTO_GRAL_RFC,
    TIPO_DOCUMENTO_GRAL_RFC
  ),
)


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
        return "{} {} {}".format(
            self.last_name,
            self.apellido_materno,
            self.first_name,
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


class HistoriaLaboral(models.Model):
    idhistorialaboral = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE,
        related_name='historia')
    comentarios = models.TextField(blank=True)
    uma = models.ForeignKey(
        'UMA', on_delete=models.PROTECT, related_name='+', default=getmaxUMA)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    DataFrameDays = None
    DataFramePeriod = None
    DataFrameGraph = None

    @property
    def dias_cotizados(self):
        return self.data_table_period()['subtotal']['dias_cotizados']

    @property
    def semanas_cotizadas(self):
        return self.dias_cotizados / 7

    def data_table_days(self):
        if self.DataFrameDays:
            return self.DataFrameDays
        df_day = pd.DataFrame(columns=['fecha', 'empresa', 'salario_base'])
        for reg in self.registros.all():
            for det in reg.detalle.all():
                df_day = df_day.append(pd.DataFrame({
                    'fecha': pd.date_range(det.inicio, det.fin),
                    'empresa': "{}\n".format(reg),
                    'salario_base': det.salario_base,
                }), ignore_index=True)
        df_day = df_day.sort_values(by=['fecha', 'empresa'])
        self.DataFrameDays = df_day
        return self.DataFrameDays

    def data_table_period(self):
        if self.DataFramePeriod:
            return self.DataFramePeriod
        df = pd.DataFrame(columns=[
            'empresa',
            'inicio', 'fin', 'dias_cotizados', 'semanas_cotizadas',
            'salario_base', 'suma_salario', 'salario_comentario'])
        tope_uma = 25 * self.uma.valor
        df_day = self.data_table_days()
        fecha_inicio = None
        fecha_fin = None
        empresa = None
        salario_base = None
        fecha_inicio_ant = None
        fecha_fin_ant = None
        empresa_ant = None
        salario_base_ant = None
        for reg in df_day.groupby(['fecha']).agg(['sum']).iterrows():
            r_fecha, r_empresa, r_salario_base = reg[0], reg[1][0], reg[1][1]
            if fecha_inicio is None:
                fecha_inicio = r_fecha
            fecha_fin = r_fecha
            if empresa is None:
                empresa = r_empresa
            if salario_base is None:
                salario_base = r_salario_base
            if empresa != r_empresa or salario_base != r_salario_base:
                dc = (fecha_fin_ant - fecha_inicio_ant).days + 1
                sb = salario_base_ant
                sb_commentario = ''
                if sb > tope_uma:
                    sb_commentario = (
                        "El salario base es de ${} pero "
                        "el tope UMA es de ${}").format(sb, tope_uma)
                    sb = tope_uma
                df = df.append({
                    'empresa': empresa_ant,
                    'inicio': fecha_inicio_ant,
                    'fin': fecha_fin_ant,
                    'salario_base': sb,
                    'salario_comentario': sb_commentario,
                    'dias_cotizados': dc,
                    'semanas_cotizadas': dc / 7,
                    'suma_salario': sb * dc,
                    }, ignore_index=True)
                fecha_inicio = r_fecha
                empresa = r_empresa
                salario_base = r_salario_base
            else:
                fecha_inicio_ant = fecha_inicio
                fecha_fin_ant = fecha_fin
                empresa_ant = empresa
                salario_base_ant = salario_base
        if fecha_fin_ant and fecha_inicio_ant:
            dc = (fecha_fin_ant - fecha_inicio_ant).days + 1
            sb = salario_base_ant
            sb_commentario = ''
            if sb > tope_uma:
                sb_commentario = (
                    "El salario base es de ${} pero el "
                    "tope UMA es de ${}").format(sb, tope_uma)
                sb = tope_uma
            df = df.append({
                'empresa': empresa_ant,
                'inicio': fecha_inicio_ant,
                'fin': fecha_fin_ant,
                'salario_base': sb,
                'salario_comentario': sb_commentario,
                'dias_cotizados': dc,
                'semanas_cotizadas': dc / 7,
                'suma_salario': sb * dc,
                }, ignore_index=True)
        df = df.sort_values(by=['inicio', 'fin', 'empresa'])
        subt = df.agg(['sum', 'min', 'max'])
        subtotal = {
            'inicio': subt['inicio'][1],
            'fin': subt['fin'][2],
            'dias_cotizados': subt['dias_cotizados'][0],
            'semanas_cotizadas': subt['semanas_cotizadas'][0],
            'suma_salario': subt['suma_salario'][0],
            }
        subtotal['salario_promedio'] = subtotal['suma_salario'] \
            / subtotal['dias_cotizados']
        self.DataFramePeriod = {
            'data': df,
            'subtotal': subtotal,
            }
        return self.DataFramePeriod

    def data_table_graph(self):
        if self.DataFrameGraph:
            return self.DataFrameGraph
        dtp = self.data_table_period()
        inicio = date(
            dtp['subtotal']['inicio'].year,
            dtp['subtotal']['inicio'].month,
            dtp['subtotal']['inicio'].day)
        fin = date(
            dtp['subtotal']['fin'].year,
            dtp['subtotal']['fin'].month,
            dtp['subtotal']['fin'].day)
        dias = (fin - inicio).days + 1
        data = []
        for reg in self.registros.all():
            periodos = []
            for det in reg.detalle.all():
                pdias = (det.fin - det.inicio).days + 1
                dias_from_start = (det.inicio - inicio).days
                periodos.append({
                    'inicio': det.inicio.strftime('%d/%m/%Y'),
                    'fin': det.fin.strftime('%d/%m/%Y'),
                    'salario_base': float(det.salario_base),
                    'dias': pdias,
                    'porc': float(pdias * 100 / dias),
                    'porc_from_start': float(dias_from_start * 100 / dias)
                    })
            data.append({'empresa': "{}".format(reg), 'periodos': periodos})
        self.DataFrameGraph = {
            'data_table_period': dtp,
            'data_table_graph': data,
            'dias': dias}
        return self.DataFrameGraph

    class Meta:
        ordering = ["cliente", "-updated_at"]

    def __str__(self):
        return "Historia Laboral {} ({})".format(self.cliente, self.uma)

    def __unicode__(self):
        return self.__str__()


class HistoriaLaboralRegistro(models.Model):
    idhistorialaboralregistro = models.AutoField(primary_key=True)
    historia_laboral = models.ForeignKey(
        HistoriaLaboral, on_delete=models.CASCADE,
        related_name='registros')
    registro_patronal = models.CharField(blank=True, max_length=15)
    empresa = models.CharField(blank=True, max_length=200)
    fecha_de_alta = models.DateField(null=True, blank=True)
    fecha_de_baja = models.DateField(null=True, blank=True)
    vigente = models.BooleanField(default=False, blank=True)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def salario_base(self):
        return self.detalle.all()[0].salario_base

    @property
    def dias_cotizados(self):
        dias = 0
        for det in self.detalle.all():
            dias += det.dias_cotizados
        return dias

    @property
    def semanas_cotizadas(self):
        return self.dias_cotizados / 7

    @property
    def anios_cotizados(self):
        return self.dias_cotizados / 365

    @property
    def dias_inactivos(self):
        dias = (self.fin - self.inicio).days
        dc = dias - self.dias_cotizados
        if dc < 0:
            dc = 0
        return dc

    @property
    def semanas_inactivos(self):
        return self.dias_inactivos / 7

    @property
    def anios_inactivos(self):
        return self.dias_inactivos / 365

    @property
    def inicio(self):
        return date(
            self.fecha_de_alta.year,
            self.fecha_de_alta.month,
            self.fecha_de_alta.day)

    @property
    def fin(self):
        if self.vigente:
            return date.today()
        else:
            return date(
                self.fecha_de_baja.year,
                self.fecha_de_baja.month,
                self.fecha_de_baja.day)

    def setDates(self):
        vigente = False
        fecha_inicial = self.detalle.all().aggregate(Min('fecha_inicial'))
        fecha_final = self.detalle.all().aggregate(Max('fecha_final'))
        for det in self.detalle.all():
            vigente = vigente or det.vigente
        self.vigente = vigente
        self.fecha_de_alta = fecha_inicial['fecha_inicial__min']
        if not vigente:
            self.fecha_de_baja = fecha_final['fecha_final__max']
        else:
            self.fecha_de_baja = None
        self.save()

    class Meta:
        ordering = ["historia_laboral", "-fecha_de_alta", "-fecha_de_baja"]

    def __str__(self):
        res = ""
        if self.empresa and self.registro_patronal:
            res = "{} ({})".format(
                self.empresa.strip(), self.registro_patronal.strip())
        elif self.empresa:
            res = "{}".format(self.empresa.strip())
        elif self.registro_patronal:
            res = "{}".format(self.registro_patronal.strip())
        return res.strip()

    def __unicode__(self):
        return self.__str__()

# Tipos de Movimiento

# Reingreso
# Modificacion de Salario
# Baja


class HistoriaLaboralRegistroDetalle(models.Model):
    idhistorialaboralregistrodetalle = models.AutoField(primary_key=True)
    historia_laboral_registro = models.ForeignKey(
        HistoriaLaboralRegistro, on_delete=models.CASCADE,
        related_name='detalle')
    fecha_inicial = models.DateField(null=True)
    fecha_final = models.DateField(null=True, blank=True)
    vigente = models.BooleanField(default=False, blank=True)
    # Salario base es diario
    salario_base = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.0)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def inicio(self):
        return date(
            self.fecha_inicial.year,
            self.fecha_inicial.month,
            self.fecha_inicial.day)

    @property
    def fin(self):
        if self.vigente:
            return date.today()
        else:
            return date(
                self.fecha_final.year,
                self.fecha_final.month,
                self.fecha_final.day)

    @property
    def dias_cotizados(self):
        return (self.fin - self.inicio).days + 1

    @property
    def semanas_cotizadas(self):
        return self.dias_cotizados / 7

    @property
    def anios_cotizados(self):
        return self.dias_cotizados / 365

    class Meta:
        ordering = [
            "historia_laboral_registro",
            "-fecha_inicial",
            "-fecha_final"
        ]

    def __str__(self):
        return "{}-{}".format(self.fecha_inicial, self.fecha_final)

    def __unicode__(self):
        return self.__str__()


class UMA(models.Model):
    iduma = models.AutoField(primary_key=True)
    año = models.PositiveSmallIntegerField(default=getyear, unique=True)
    valor = models.DecimalField(max_digits=5, decimal_places=2)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-año']

    def __str__(self):
        return "{}".format(self.año)

    def __unicode__(self):
        return self.__str__()


class Cuantiabasica(models.Model):
    idcuantia = models.AutoField(primary_key=True)
    salario_inicio = models.DecimalField(max_digits=6, decimal_places=4)
    salario_fin = models.DecimalField(max_digits=6, decimal_places=4)
    porcentaje_de_cuantia_basica = models.DecimalField(
        max_digits=5, decimal_places=3)
    porcentaje_de_incremento_anual = models.DecimalField(
        max_digits=5, decimal_places=3)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['salario_inicio', 'salario_fin']

    def __str__(self):
        return "de {} a {}".format(self.salario_inicio, self.salario_fin)

    def __unicode__(self):
        return self.__str__()


class Factoredad(models.Model):
    idfactoredad = models.AutoField(primary_key=True)
    edad = models.PositiveSmallIntegerField()
    factor_de_edad = models.DecimalField(max_digits=6, decimal_places=3)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['edad']

    def __str__(self):
        return "{} ({}%%)".format(self.edad, self.factor_de_edad)

    def __unicode__(self):
        return self.__str__()
