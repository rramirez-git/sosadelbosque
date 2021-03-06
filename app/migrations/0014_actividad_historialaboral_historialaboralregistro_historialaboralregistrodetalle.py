# Generated by Django 2.1.7 on 2019-04-23 23:36

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('initsys', '0002_auto_20190409_1910'),
        ('app', '0013_merge_20190417_0209'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('idactividad', models.AutoField(primary_key=True, serialize=False)),
                ('titulo', models.CharField(max_length=150)),
                ('comenatrios', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actividades_asociadas', to='app.Cliente')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='initsys.Usr')),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='actividades', to='app.EstatusActividad')),
                ('tipo_de_actividad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='actividades_de_tipo', to='app.TipoActividad')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='initsys.Usr')),
            ],
            options={
                'ordering': ['estado', '-updated_at', 'cliente'],
            },
        ),
        migrations.CreateModel(
            name='HistoriaLaboral',
            fields=[
                ('idhistorialaboral', models.AutoField(primary_key=True, serialize=False)),
                ('comenatrios', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actividades', to='app.Cliente')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='initsys.Usr')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='initsys.Usr')),
            ],
            options={
                'ordering': ['cliente', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='HistoriaLaboralRegistro',
            fields=[
                ('idhistorialaboralregistro', models.AutoField(primary_key=True, serialize=False)),
                ('registro_patronal', models.CharField(blank=True, max_length=15)),
                ('empresa', models.CharField(blank=True, max_length=200)),
                ('fecha_de_alta', models.DateField(default=datetime.date.today)),
                ('fecha_de_baja', models.DateField(default=datetime.date.today)),
                ('historia_laboral', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registros', to='app.HistoriaLaboral')),
            ],
            options={
                'ordering': ['historia_laboral', '-fecha_de_alta', '-fecha_de_baja'],
            },
        ),
        migrations.CreateModel(
            name='HistoriaLaboralRegistroDetalle',
            fields=[
                ('idhistorialaboralregistrodetalle', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_inicial', models.DateField(default=datetime.date.today)),
                ('fecha_final', models.DateField(default=datetime.date.today)),
                ('salario_base', models.DecimalField(decimal_places=2, default=0.0, max_digits=7)),
                ('historia_laboral_registro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalle', to='app.HistoriaLaboralRegistro')),
            ],
            options={
                'ordering': ['historia_laboral_registro', '-fecha_inicial', '-fecha_final'],
            },
        ),
    ]
