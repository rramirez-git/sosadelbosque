# Generated by Django 2.1.7 on 2019-04-10 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20190409_1910'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='observaciones',
            field=models.TextField(blank=True),
        ),
    ]