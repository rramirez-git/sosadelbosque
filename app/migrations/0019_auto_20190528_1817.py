# Generated by Django 2.1.7 on 2019-05-28 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20190528_1759'),
    ]

    operations = [
        migrations.AddField(
            model_name='estatusactividad',
            name='mostrar_en_panel',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='taxonomiaexpediente',
            name='mostrar_en_panel',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]