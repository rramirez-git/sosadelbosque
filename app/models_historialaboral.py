from django.db import models
import pandas as pd
from django.db.models import Max, Min, Sum

from .models_cliente import *
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


def getyear():
    return date.today().year


def getmaxUMA():
    try:
        return UMA.objects.all()[0].pk
    except IndexError:
        return 0


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
    factor_de_actualizacion = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=1.11, verbose_name="Factor de Actualización")
    tiene_esposa = models.BooleanField(
        default=True, verbose_name="Asignacion Familiar (15%)")
    numero_de_hijos = models.PositiveSmallIntegerField(
        default=0, verbose_name="Número de Hijos")
    semanas_descontar = models.PositiveSmallIntegerField(
        default=0, verbose_name="Número de Semanas a Descontar"
    )
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    df_agg_salario = None

    @property
    def dias_cotizados(self):
        df_pers = df_load_HLRD_periodo_continuo_laborado(self.cliente.pk)
        res = df_pers.agg(['sum'])['dias_cotiz']['sum']
        if res is None:
            res = 0
        for reg in self.registros_supuesto.all():
            res += reg.dias_cotizados
        return res - (7 * self.semanas_descontar)

    @property
    def semanas_cotizadas(self):
        df_pers = df_load_HLRD_periodo_continuo_laborado(self.cliente.pk)
        res = df_pers.agg(['sum'])['semanas_cotiz']['sum']
        if res is None:
            res = 0
        for reg in self.registros_supuesto.all():
            res += reg.semanas_cotizadas
        return res - self.semanas_descontar

    @property
    def inicio(self):
        df_pers = df_load_HLRD_periodo_continuo_laborado(self.cliente.pk)
        res = df_pers.agg(['min'])['fecha_inicio']['min'].date()
        for reg in self.registros_supuesto.all():
            if reg.fecha_de_alta < res:
                res = reg.fecha_de_alta
        return res

    @property
    def fin(self):
        df_pers = df_load_HLRD_periodo_continuo_laborado(self.cliente.pk)
        res = df_pers.agg(['max'])['fecha_fin']['max'].date()
        for reg in self.registros_supuesto.all():
            if reg.fecha_de_baja > res:
                res = reg.fecha_de_baja
        return res

    def agg_salario(self, dias_calculo=None):
        """
        Calcula los elementos relacionados con el Salario Promedio Diario

        Parameters
        ----------
        dias_calculo : integer, optional
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
                        'f_ini', 'f_fin', 'n',
                        'salario', 'salario_topado', 'suma_salario'
                    ]),
            }

            for reg in salario_df.itertuples():
                print(reg[1],reg[2],reg[3],reg[4],reg[5])
        """
        if dias_calculo is None:
            dias_calculo = self.dias_salario_promedio
        if self.df_agg_salario is not None:
            return self.df_agg_salario
        df = df_load_HLRDDay_agg(self.cliente.pk).head(dias_calculo)
        for reg in self.registros_supuesto.all():
            for det in reg.detalle.all():
                for dt in pd.date_range(det.inicio, det.fin):
                    df = df.append([{'fecha': dt, 'salario': det.salario_base}], ignore_index=True)
        df.sort_values(by='fecha', ascending=False, inplace=True)
        df = df.head(dias_calculo)
        tope_uma = 25 * self.uma.valor
        df['salario_topado'] = df.salario
        df.loc[df.salario > tope_uma, 'salario_topado'] = tope_uma
        df["salario_topado"] = pd.to_numeric(df["salario_topado"])
        ss = df.agg(['sum', 'min', 'max'])
        periodos = []
        inicio = None
        fin = None
        salario = None
        salario_topado = None
        for reg in df.sort_values(by='fecha', ascending=True).itertuples():
            if inicio is None:
                inicio = reg[1]
            if fin is None:
                fin = reg[1]
            if salario is None:
                salario = reg[2]
            if salario_topado is None:
                salario_topado = reg[3]
            if (reg[1] - fin).days > 1 or salario != reg[2]:
                dias = (fin - inicio).days + 1
                periodos.append({
                    'f_ini': inicio,
                    'f_fin': fin,
                    'n': dias,
                    'salario': salario,
                    'salario_topado': salario_topado,
                    'suma_salario': dias * salario_topado})
                inicio = reg[1]
                salario = reg[2]
                salario_topado = reg[3]
            fin = reg[1]
        dias = (fin - inicio).days + 1
        periodos.append({
            'f_ini': inicio,
            'f_fin': fin,
            'n': dias,
            'salario': salario,
            'salario_topado': salario_topado,
            'suma_salario': dias * salario_topado})
        salary_df = pd.DataFrame(periodos, columns=[
            'f_ini', 'f_fin', 'n',
            'salario', 'salario_topado', 'suma_salario'
            ]).sort_values(['f_ini', 'f_fin'], ascending=[False, False])
        self.df_agg_salario = {
            'suma_salario': ss['salario_topado']['sum'],
            'salario_promedio': ss['salario_topado']['sum'] / dias_calculo,
            'fecha_minima': ss['fecha']['min'],
            'fecha_maxima': ss['fecha']['max'],
            'salario_df': salary_df,
        }
        return self.df_agg_salario

    def reset_and_calculate_history(self):
        for reg in self.registros.all():
            reg.setFechasIniFin(False)
        df_reset_data(self.cliente.pk, self)

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
    color = models.CharField(max_length=15, default=BootstrapColors[2][0], choices=BootstrapColors)
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
        df_pers = df_load_HLRD_periodo_continuo_laborado(
            self.historia_laboral.cliente.pk)
        df_pers = df_pers[df_pers.historialaboralregistro_pk == self.pk]
        res = df_pers.agg(['sum'])['dias_cotiz']['sum']
        if res is None:
            return 0
        return res

    @property
    def semanas_cotizadas(self):
        df_pers = df_load_HLRD_periodo_continuo_laborado(
            self.historia_laboral.cliente.pk)
        df_pers = df_pers[df_pers.historialaboralregistro_pk == self.pk]
        res = df_pers.agg(['sum'])['semanas_cotiz']['sum']
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
        try:
            return date(
                self.fecha_de_alta.year,
                self.fecha_de_alta.month,
                self.fecha_de_alta.day)
        except AttributeError:
            return date.today()

    @property
    def fin(self):
        if self.vigente:
            return date.today()
        else:
            try:
                return date(
                    self.fecha_de_baja.year,
                    self.fecha_de_baja.month,
                    self.fecha_de_baja.day)
            except AttributeError:
                return date.today()

    def setFechasIniFin(self, filling_days=True):
        vigente = False
        fecha_inicial = self.detalle.all().aggregate(Min('fecha_inicial'))
        fecha_final = self.detalle.all().aggregate(Max('fecha_final'))
        for det in self.detalle.all():
            vigente = vigente or det.vigente
            if filling_days:
                det.fill_days()
        self.vigente = vigente
        self.fecha_de_alta = fecha_inicial['fecha_inicial__min']
        if not vigente:
            self.fecha_de_baja = fecha_final['fecha_final__max']
        else:
            self.fecha_de_baja = None
        self.save()

    def setDates(self):
        self.setFechasIniFin()
        self.createPeriodos()

    def createPeriodos(self):
        df_pers = df_load_HLRD_periodo_continuo_laborado(
            self.historia_laboral.cliente.pk)
        df_pers_new = df_generate_HLRD_periodo_continuo_laborado(
            self.historia_laboral.cliente.pk, self)
        df_pers = df_update(df_pers, df_pers_new, reg=self.pk)
        df_save_HLRD_periodo_continuo_laborado(
            self.historia_laboral.cliente.pk, df_pers)
        df_pers = df_generate_data_cotiz_HLRD_periodo_continuo_laborado(
            self.historia_laboral.cliente.pk)
        df_save_HLRD_periodo_continuo_laborado(
            self.historia_laboral.cliente.pk, df_pers)

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
        reg = self.historia_laboral_registro
        df_day = df_load_HLRDDay(reg.historia_laboral.cliente.pk)
        df_day = df_update(df_day, df_data_generate_HLRDDay(self), det=self.pk)
        df_save_HLRDDay(reg.historia_laboral.cliente.pk, df_day)

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


class HistoriaLaboralRegistroSupuesto(models.Model):
    idhistorialaboralregistrosupuesto = models.AutoField(primary_key=True)
    historia_laboral = models.ForeignKey(
        HistoriaLaboral, on_delete=models.CASCADE,
        related_name='registros_supuesto')
    registro_patronal = models.CharField(blank=True, max_length=15, default="")
    empresa = models.CharField(blank=True, max_length=200, default="Supuesto")
    fecha_de_alta = models.DateField(null=True, blank=True)
    fecha_de_baja = models.DateField(null=True, blank=True)
    vigente = models.BooleanField(default=False, blank=True)
    color = models.CharField(max_length=15, default=BootstrapColors[1][0], choices=BootstrapColors)
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
        res = 0
        for det in self.detalle.all():
            res += det.dias_cotizados
        return res

    @property
    def semanas_cotizadas(self):
        res = 0
        for det in self.detalle.all():
            res += det.semanas_cotizadas
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
        try:
            return date(
                self.fecha_de_alta.year,
                self.fecha_de_alta.month,
                self.fecha_de_alta.day)
        except AttributeError:
            return date.today()

    @property
    def fin(self):
        if self.vigente:
            return date.today()
        else:
            try:
                return date(
                    self.fecha_de_baja.year,
                    self.fecha_de_baja.month,
                    self.fecha_de_baja.day)
            except AttributeError:
                return date.today()

    def setFechasIniFin(self):
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

    def setDates(self):
        self.setFechasIniFin()

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


class HistoriaLaboralRegistroDetalleSupuesto(models.Model):
    idhistorialaboralregistrodetalle = models.AutoField(primary_key=True)
    historia_laboral_registro_supuesto = models.ForeignKey(
        HistoriaLaboralRegistroSupuesto, on_delete=models.CASCADE,
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

    class Meta:
        ordering = [
            "historia_laboral_registro_supuesto",
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
        return "{} ({}%)".format(self.edad, self.factor_de_edad)

    def __unicode__(self):
        return self.__str__()


class OpcionPension(models.Model):
    idopcionpension = models.AutoField(primary_key=True)
    historia_laboral = models.ForeignKey(
        HistoriaLaboral, on_delete=models.CASCADE,
        related_name='opciones')
    seleccionada = models.BooleanField(default=False)
    uma_anio = models.PositiveSmallIntegerField()
    uma_valor = models.DecimalField(max_digits=5, decimal_places=2)
    salario_promedio = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.0)
    salario_promedio_mensual = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.0)
    dias_calculo_saldo_promedio = models.PositiveSmallIntegerField()
    semanas_cotizadas = models.PositiveSmallIntegerField()
    porcentaje_cuantia_basica = models.DecimalField(
        max_digits=6, decimal_places=3)
    porcentaje_incremento_anual = models.DecimalField(
        max_digits=6, decimal_places=3)
    edad = models.PositiveSmallIntegerField()
    porcentaje_factor_edad = models.DecimalField(
        max_digits=6, decimal_places=3)
    porcentaje_cuantia_basica_incremento = models.DecimalField(
        max_digits=6, decimal_places=3)
    factor_actualizacion = models.DecimalField(
        max_digits=6, decimal_places=3)
    porcentaje_esposa = models.DecimalField(
        max_digits=6, decimal_places=3)
    porcentaje_hijos = models.DecimalField(
        max_digits=6, decimal_places=3)
    porcentaje_asignaciones_familiares = models.DecimalField(
        max_digits=6, decimal_places=3)
    pension_mensual_calculada = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.0)
    porcentaje_de_salario_promedio = models.DecimalField(
        max_digits=6, decimal_places=3)
    comentarios = models.TextField(blank=True)
    created_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        Usr, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-seleccionada', 'created_at']

    def __str__(self):
        return "{} ({})".format(self.historia_laboral.cliente, self.created_at)

    def __unicode__(self):
        return self.__str__()
