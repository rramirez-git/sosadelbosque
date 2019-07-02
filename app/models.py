from django.db import models
from django.db.models import Max, Min, Sum
from datetime import date, timedelta

import pandas as pd
import sys

from initsys.models import Usr, Direccion
from routines.utils import BootstrapColors, inter_periods_days, free_days

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
    dias_salario_promedio = models.PositiveSmallIntegerField(
        default=1750,
        verbose_name="Cantidad de Días para calculo de salario promedio")
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def dias_cotizados(self):
        res = self.hlrd_periodos_continuo_levelhl_hl.aggregate(
            Sum('dias'))['dias__sum']
        if res is None:
            return 0
        return res

    @property
    def semanas_cotizadas(self):
        res = self.hlrd_periodos_continuo_levelhl_hl.aggregate(
            Sum('semanas'))['semanas__sum']
        if res is None:
            return 0
        return res

    @property
    def inicio(self):
        res = self.hlrd_periodos_continuo_levelhl_hl.aggregate(
            Min('fecha_inicio'))['fecha_inicio__min']
        return res

    @property
    def fin(self):
        res = self.hlrd_periodos_continuo_levelhl_hl.aggregate(
            Max('fecha_fin'))['fecha_fin__max']
        return res

    def agg_salario(self, dias=None):
        """
        Calcula los elementos relacionados con el Salario Promedio Diario

        Parameters
        ----------
        dias : integer, optional
            Número de últimos días para realizar el cálculo del
            Salario Promedio Diario, si su valor es None se tomará en
            cuenta el valor establecido en el miembro dias_salario_promedio

        Returns
        -------
        dict
            diccionario con la estructura de datos relacionada con el
            cálculo del Salario Promedio Diario:

            {
                'suma_salario': Decimal,
                'salario_promedio': Decimal,
                'fecha_minima': Date,
                'fecha_maxima': Date,
                'salario_df': pandas.DataFrame(
                    columns=[
                        'f_ini', 'f_fin', 'n', 'salario', 'suma_salario'
                    ]),
            }

            for reg in salario_df.itertuples():
                print(reg[1],reg[2],reg[3],reg[4],reg[5])
        """
        if dias is None:
            dias = self.dias_salario_promedio
        df = pd.DataFrame(self.hlrd_days_hl.values('fecha').annotate(
            suma_salario=Sum('salario_base')).order_by('-fecha')[:dias])
        ss = df.agg(['sum', 'min', 'max'])
        salary_df = pd.DataFrame(
            [(r[1], r[2], r[3], r[0], r[3] * r[0]) for r in df.groupby(
                ['suma_salario']).agg(
                    ['min', 'max', 'count']).itertuples()],
            columns=['f_ini', 'f_fin', 'n', 'salario', 'suma_salario']
            ).sort_values(['f_ini', 'f_fin'])
        # >>> for reg in salary_df.itertuples():
        # ...     print(reg[1],reg[2],reg[3],reg[4],reg[5])
        return {
            'suma_salario': ss['suma_salario']['sum'],
            'salario_promedio': ss['suma_salario']['sum'] / dias,
            'fecha_minima': ss['fecha']['min'],
            'fecha_maxima': ss['fecha']['max'],
            'salario_df': salary_df,
        }

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
        try:
            return self.detalle.all()[0].salario_base
        except IndexError:
            return 0.0

    @property
    def dias_cotizados(self):
        res = self.hlrd_periodos_continuo_reg.aggregate(
            Sum('dias'))['dias__sum']
        if res is None:
            return 0
        return res

    @property
    def semanas_cotizadas(self):
        res = self.hlrd_periodos_continuo_reg.aggregate(
            Sum('semanas'))['semanas__sum']
        if res is None:
            return 0
        return res

    @property
    def anios_cotizados(self):
        return round(self.semanas_cotizadas / 52, 2)

    @property
    def dias_inactivos(self):
        dias = (self.fin - self.inicio).days
        dc = dias - self.dias_cotizados
        if dc < 0:
            dc = 0
        return dc

    @property
    def semanas_inactivos(self):
        return round(self.dias_inactivos / 7)

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
            det.fill_days()
        self.vigente = vigente
        self.fecha_de_alta = fecha_inicial['fecha_inicial__min']
        if not vigente:
            self.fecha_de_baja = fecha_final['fecha_final__max']
        else:
            self.fecha_de_baja = None
        self.save()
        self.createPeriodos()

    def createPeriodos(self):
        self.hlrd_periodos_continuo_reg.all().delete()
        fecha_ini = None
        fecha_ant = None
        for reg in list(self.hlrd_days_reg.all()):
            if fecha_ini is None:
                fecha_ini = reg.fecha
            if fecha_ant is None:
                fecha_ant = reg.fecha
            if reg.fecha > fecha_ant + timedelta(days=1):
                d = (fecha_ant - fecha_ini).days + 1
                s = round(d / 7)
                a = s / 52
                HLRD_periodo_continuo_laborado.objects.create(
                    historialaboralregistro=self,
                    historialaboral=self.historia_laboral,
                    fecha_inicio=fecha_ini,
                    fecha_fin=fecha_ant,
                    dias=d,
                    semanas=s,
                    anios=a)
                fecha_ini = reg.fecha
            fecha_ant = reg.fecha
        d = (fecha_ant - fecha_ini).days + 1
        s = round(d / 7)
        a = s / 52
        HLRD_periodo_continuo_laborado.objects.create(
            historialaboralregistro=self,
            historialaboral=self.historia_laboral,
            fecha_inicio=fecha_ini,
            fecha_fin=fecha_ant,
            dias=d,
            semanas=s,
            anios=a)
        hl = self.historia_laboral
        pers = list(hl.hlrd_periodos_continuo_hl.all())
        for x in range(len(pers)):
            dias_cotizados = pers[x].dias
            dias_inactivos = sys.maxsize
            if 0 == x:
                dias_inactivos = 0
            else:
                for y in range(len(pers)):
                    if y < x:
                        dias_c = len(free_days(
                            pers[y].fecha_inicio,
                            pers[y].fecha_fin,
                            pers[x].fecha_inicio,
                            pers[x].fecha_fin))
                        if dias_cotizados > dias_c:
                            dias_cotizados = dias_c
                        dias_i = inter_periods_days(
                            pers[y].fecha_inicio,
                            pers[y].fecha_fin,
                            pers[x].fecha_inicio,
                            pers[x].fecha_fin)
                        if dias_inactivos > dias_i:
                            dias_inactivos = dias_i
            pers[x].dias_cotiz = dias_cotizados
            pers[x].semanas_cotiz = round(dias_cotizados / 7)
            pers[x].anios_cotiz = round(dias_cotizados / 7) / 52
            pers[x].dias_inact = dias_inactivos
            pers[x].semanas_inact = round(dias_inactivos / 7)
            pers[x].anios_inact = round(dias_inactivos / 7) / 52
            pers[x].save()
        hl.hlrd_periodos_continuo_levelhl_hl.all().delete()
        fecha_ini = None
        fecha_ant = None
        for reg in list(hl.hlrd_days_hl.all()):
            if fecha_ini is None:
                fecha_ini = reg.fecha
            if fecha_ant is None:
                fecha_ant = reg.fecha
            if reg.fecha > fecha_ant + timedelta(days=1):
                d = (fecha_ant - fecha_ini).days + 1
                HLRD_periodo_continuo_laborado_levelhl.objects.create(
                    historialaboral=hl,
                    fecha_inicio=fecha_ini,
                    fecha_fin=fecha_ant,
                    dias=d,
                    semanas=round(d / 7))
                fecha_ini = reg.fecha
            fecha_ant = reg.fecha
        d = (fecha_ant - fecha_ini).days + 1
        HLRD_periodo_continuo_laborado_levelhl.objects.create(
            historialaboral=hl,
            fecha_inicio=fecha_ini,
            fecha_fin=fecha_ant,
            dias=d,
            semanas=round(d / 7))

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
        return round(self.dias_cotizados / 7)

    @property
    def anios_cotizados(self):
        return round(self.semanas_cotizadas / 52, 2)

    def fill_days(self):
        self.hlrd_days_det.all().delete()
        reg = self.historia_laboral_registro
        for dt in pd.date_range(self.inicio, self.fin):
            HLRDDay.objects.create(
                historialaboralregistrodetalle=self,
                historialaboralregistro=reg,
                historialaboral=reg.historia_laboral,
                fecha=dt,
                salario_base=self.salario_base)

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


class HLRDDay(models.Model):
    idhlrdday = models.AutoField(primary_key=True)
    historialaboralregistrodetalle = models.ForeignKey(
        HistoriaLaboralRegistroDetalle, models.CASCADE, 'hlrd_days_det')
    historialaboralregistro = models.ForeignKey(
        HistoriaLaboralRegistro, models.CASCADE, 'hlrd_days_reg')
    historialaboral = models.ForeignKey(
        HistoriaLaboral, models.CASCADE, 'hlrd_days_hl')
    fecha = models.DateField()
    salario_base = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.0)

    class Meta:
        ordering = [
            "fecha",
        ]

    def __str__(self):
        return "{}: {}".format(self.fecha, self.salario_base)

    def __unicode__(self):
        return self.__str__()


class HLRD_periodo_continuo_laborado(models.Model):
    idhlrd_periodo_continuo_laborado = models.AutoField(primary_key=True)
    historialaboralregistro = models.ForeignKey(
        HistoriaLaboralRegistro, models.CASCADE,
        'hlrd_periodos_continuo_reg')
    historialaboral = models.ForeignKey(
        HistoriaLaboral, models.CASCADE, 'hlrd_periodos_continuo_hl')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias = models.PositiveSmallIntegerField()
    semanas = models.PositiveIntegerField()
    anios = models.DecimalField(max_digits=4,decimal_places=2)
    dias_cotiz = models.PositiveSmallIntegerField(default=0)
    semanas_cotiz = models.PositiveIntegerField(default=0)
    anios_cotiz = models.DecimalField(
        max_digits=4, decimal_places=2, default=0)
    dias_inact = models.PositiveSmallIntegerField(default=0)
    semanas_inact = models.PositiveIntegerField(default=0)
    anios_inact = models.DecimalField(
        max_digits=4, decimal_places=2, default=0)

    class Meta:
        ordering = [
            "fecha_inicio",
            "fecha_fin",
        ]


class HLRD_periodo_continuo_laborado_levelhl(models.Model):
    idhlrd_periodo_continuo_laborado_levelhl = models.AutoField(
        primary_key=True)
    historialaboral = models.ForeignKey(
        HistoriaLaboral, models.CASCADE, 'hlrd_periodos_continuo_levelhl_hl')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias = models.PositiveSmallIntegerField()
    semanas = models.PositiveIntegerField()

    class Meta:
        ordering = [
            "fecha_inicio",
            "fecha_fin",
        ]
