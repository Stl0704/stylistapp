# Generated by Django 5.0.3 on 2024-06-10 05:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="local",
            old_name="direcciones",
            new_name="nombre",
        ),
        migrations.RemoveField(
            model_name="local",
            name="nombre_local",
        ),
        migrations.AddField(
            model_name="local",
            name="direccion",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="local",
            name="prestador",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="local",
                to="api.prestadorservicios",
            ),
        ),
    ]
