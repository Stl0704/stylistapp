# Generated by Django 5.0.3 on 2024-06-16 05:22

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_alter_comuna_poblacion"),
    ]

    operations = [
        migrations.AddField(
            model_name="historialcompra",
            name="fecha_registro",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
