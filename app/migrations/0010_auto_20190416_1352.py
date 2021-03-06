# Generated by Django 2.1.7 on 2019-04-16 18:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('initsys', '0002_auto_20190409_1910'),
        ('app', '0009_auto_20190409_1953'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstatusActividad',
            fields=[
                ('idestatusactividad', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='initsys.Usr')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='initsys.Usr')),
            ],
            options={
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='TipoActividad',
            fields=[
                ('idtipoactividad', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='initsys.Usr')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='initsys.Usr')),
            ],
            options={
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='TipoDocumento',
            fields=[
                ('idtipodocumento', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('visible_para_usuario', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='initsys.Usr')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='initsys.Usr')),
            ],
            options={
                'ordering': ['nombre'],
            },
        ),
        migrations.AddField(
            model_name='doctogral',
            name='tipo_de_documento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='documentos', to='app.TipoDocumento'),
            preserve_default=False,
        ),
    ]
