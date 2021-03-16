from django.db import models
from datetime import date

from .models_cliente import Cliente, Usr
from .models_actividades import MedioActividad, TipoActividad

TIPO_PROXIMO_EVTO_PENSION = 'Pensión'
TIPO_PROXIMO_EVTO_MOD40 = 'MOD 40'
TIPO_PROXIMO_EVTO = (
    (TIPO_PROXIMO_EVTO_PENSION, "Pension"),
    (TIPO_PROXIMO_EVTO_MOD40, "MOD 40"),
)

ESTATUS_ENVIO_ENVIADO = 'Enviado'
ESTATUS_ENVIO_PENDIENTE = 'Pendiente'
ESTATUS_ENVIO = (
    (ESTATUS_ENVIO_ENVIADO, 'Enviado'),
    (ESTATUS_ENVIO_PENDIENTE, 'Pendiente'),
)


class TmpReporteControlRecepcion(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='+')
    fecha_de_ultimo_contacto = models.DateField(default=date.today)
    nota = models.TextField(blank=True)
    autor = models.ForeignKey(
        Usr,
        on_delete=models.CASCADE,
        related_name='+')

    class Meta:
        ordering = ["-fecha_de_ultimo_contacto"]

    def __str__(self):
        return f"{self.fecha_de_ultimo_contacto: %d/%m/%Y}"

    def __unicode__(self):
        return self.__str__()

    @property
    def isMaxDate(self):
        return self.__class__.objects.filter(
            fecha_de_ultimo_contacto__gt=self.fecha_de_ultimo_contacto,
            cliente__idcliente__exact=self.cliente.idcliente).count() == 0


class TmpReporteControlProximoPensionMod40(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='+')
    fecha_del_evento = models.DateField(default=date.today)
    tipo = models.CharField(
        max_length=15,
        choices=TIPO_PROXIMO_EVTO,
        default=TIPO_PROXIMO_EVTO_PENSION)

    class Meta:
        ordering = ["tipo", "fecha_del_evento"]

    def __str__(self):
        return f"{self.tipo} ({self.fecha_del_evento:%d/%m/%Y})"

    def __unicode__(self):
        return self.__str__()


class TmpReporteControlPatronSustituto(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='+')
    medio = models.ForeignKey(
        MedioActividad,
        on_delete=models.PROTECT,
        related_name="+"
    )
    fecha_de_alta = models.DateField(default=date.today)
    fecha_estimada_de_baja = models.DateField(default=date.today)

    class Meta:
        ordering = ["fecha_de_alta"]

    def __str__(self):
        return f"{self.fecha_de_alta:%d/%m%Y}"

    def __unicode__(self):
        return self.__str__()


class TmpReporteControlPatronSustitutoDetalle(models.Model):
    raiz = models.ForeignKey(
        'TmpReporteControlPatronSustitutoDetalle',
        on_delete=models.CASCADE,
        related_name='detalle',
    )
    fecha_de_pago = models.DateField(default=date.today)
    cantidad = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)

    class Meta:
        ordering = ["fecha_de_pago"]

    def __str__(self):
        return f"{self.fecha_de_pago:%d/%m/%Y}"

    def __unicode__(self):
        return self.__str__()


class TmpReporteControlInscritosMod40(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='+')
    medio = models.ForeignKey(
        MedioActividad,
        on_delete=models.PROTECT,
        related_name="+"
    )
    fecha_estimada_de_baja = models.DateField(default=date.today)

    class Meta:
        ordering = ["fecha_estimada_de_baja"]

    def __str__(self):
        return f"{self.fecha_estimada_de_baja:%d/%m/%Y}"

    def __unicode__(self):
        return self.__str__()


class TmpReporteControlInscritosMod40Detalle(models.Model):
    raiz = models.ForeignKey(
        'TmpReporteControlInscritosMod40',
        on_delete=models.CASCADE,
        related_name='detalle',
    )
    fecha_de_pago = models.DateField(default=date.today)
    cantidad = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)
    linea_de_captura = models.CharField(max_length=100)
    estatus_de_envio = models.CharField(
        max_length=15,
        choices=ESTATUS_ENVIO,
        default=ESTATUS_ENVIO_PENDIENTE)

    class Meta:
        ordering = ["fecha_de_pago"]

    def __str__(self):
        return f"{self.fecha_de_pago:%d/%m/%Y}"

    def __unicode__(self):
        return self.__str__()


class TmpReportPensionesEnProceso(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='+')
    medio = models.ForeignKey(
        MedioActividad,
        on_delete=models.PROTECT,
        related_name="+"
    )
    fecha_de_envio = models.DateField(default=date.today)
    fecha_de_pago_inicial = models.DateField(default=date.today)
    fecha_de_retiro_total = models.DateField(default=date.today)

    class Meta:
        ordering = ["fecha_de_envio"]

    def __str__(self):
        return f"{self.fecha_de_envio:%d/%m/%Y}"

    def __unicode__(self):
        return self.__str__()


class TmpReportPensionesEnProcesoDetalle(models.Model):
    raiz = models.ForeignKey(
        'TmpReportPensionesEnProceso',
        on_delete=models.CASCADE,
        related_name='detalle',
    )
    prorroga_o_incorformidad = models.CharField(max_length=250)
    fecha_de_envio = models.DateField(default=date.today)
    fecha_de_correccion = models.DateField(default=date.today)

    class Meta:
        ordering = ["fecha_de_envio"]

    def __str__(self):
        return f"{self.prorroga_o_incorformidad}"

    def __unicode__(self):
        return self.__str__()


class TmpReportTramitesYCorrecciones(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='+')
    tipo_de_tramite = models.ForeignKey(
        TipoActividad,
        on_delete=models.PROTECT,
        related_name="+"
    )
    medio = models.ForeignKey(
        MedioActividad,
        on_delete=models.PROTECT,
        related_name="+"
    )
    fecha_de_envio = models.DateField(default=date.today)
    fecha_de_conclusion = models.DateField(default=date.today)
    costo = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)
    fecha_de_liquidacion = models.DateField(default=date.today)

    class Meta:
        ordering = ["fecha_de_envio"]

    def __str__(self):
        return f"{self.tipo_de_tramite} ({self.fecha_de_envio:%d/%m/%Y})"

    def __unicode__(self):
        return self.__str__()

