# Generated by Django 2.1.7 on 2019-08-13 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0040_auto_20190730_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historialaboral',
            name='tiene_esposa',
            field=models.BooleanField(default=True, verbose_name='Asignacion Familiar (15%)'),
        ),
    ]
