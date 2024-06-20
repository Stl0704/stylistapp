# Generated by Django 5.0.3 on 2024-06-20 19:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="precio_venta",
            field=models.DecimalField(decimal_places=2, default=120000, max_digits=10),
            preserve_default=False,
        ),
    ]
