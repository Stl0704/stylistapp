from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Boleta, HistorialCompra


@receiver(post_save, sender=Boleta)
def create_historial_compra(sender, instance, created, **kwargs):
    if created:
        HistorialCompra.objects.create(boleta=instance, calificacion=0)
