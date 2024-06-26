# Generated by Django 5.0.3 on 2024-04-25 06:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('cliente_id', models.CharField(max_length=45, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Genero',
            fields=[
                ('genero_id', models.CharField(max_length=45, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=45)),
                ('descripcion', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Local',
            fields=[
                ('local_id', models.CharField(max_length=45, primary_key=True, serialize=False)),
                ('nombre_local', models.CharField(max_length=45)),
                ('direcciones', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PrestadorServicios',
            fields=[
                ('prestador_serv_id', models.CharField(max_length=45, primary_key=True, serialize=False)),
                ('especialidad', models.CharField(max_length=350)),
                ('experiencia', models.CharField(max_length=450)),
                ('presentacion', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('servicio_id', models.CharField(max_length=45, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='TipoUsuario',
            fields=[
                ('tipo_user_id', models.CharField(max_length=45, primary_key=True, serialize=False)),
                ('nombre_tipo_user', models.CharField(max_length=45)),
                ('descripcion', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('user_id', models.CharField(max_length=45, primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=45)),
                ('email', models.CharField(max_length=45)),
                ('password', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Distrito',
            fields=[
                ('distrito_id', models.CharField(max_length=45, primary_key=True, serialize=False)),
                ('nombre_distrito', models.CharField(max_length=45)),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.local')),
            ],
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('persona_id', models.CharField(max_length=45, primary_key=True, serialize=False)),
                ('fecha_nac', models.DateField()),
                ('nombre', models.CharField(max_length=55)),
                ('apellido1', models.CharField(max_length=30)),
                ('apellido2', models.CharField(max_length=30)),
                ('genero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.genero')),
            ],
        ),
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('cita_id', models.CharField(max_length=45, primary_key=True, serialize=False)),
                ('fecha_hora', models.DateTimeField()),
                ('duracion', models.TimeField()),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.cliente')),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.local')),
                ('prestador_serv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.prestadorservicios')),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.servicio')),
            ],
        ),
        migrations.CreateModel(
            name='ServicioAPrestar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tarifa', models.DecimalField(decimal_places=2, max_digits=10)),
                ('disponibilidad', models.CharField(max_length=150)),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.local')),
                ('prestador_serv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.prestadorservicios')),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.servicio')),
            ],
        ),
        migrations.AddField(
            model_name='prestadorservicios',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.usuario'),
        ),
        migrations.CreateModel(
            name='PersonaUsuario',
            fields=[
                ('persona_user_id', models.AutoField(primary_key=True, serialize=False)),
                ('persona', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.persona')),
                ('tipo_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tipousuario')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.usuario')),
            ],
        ),
        migrations.AddField(
            model_name='cliente',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.usuario'),
        ),
    ]
