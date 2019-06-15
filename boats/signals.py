from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import BoatModel
from .utilities import send_activation_notofication
from django.core.signals import Signal


@receiver([post_save, post_delete], sender=BoatModel)
def invalidate_cached_lookup(sender, instance, **kwargs):
    """Инвалидация лукапа 'BoatListView'"""
    cache_key = "BoatListView"
    cache.delete(cache_key)


@receiver([post_save, post_delete], sender=BoatModel)
def invalidate_cached_lookup_boat_detail_view(sender, instance, **kwargs):
    cache_key = "boat_detail_view" + instance.boat_name
    cache.delete(cache_key)


#  ---------------------------------------------------------------------------------------------------
user_registrated = Signal(providing_args=["instance"])
"""Сигнал user_registrated #573  431  437"""


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notofication(kwargs["instance"])


user_registrated.connect(user_registrated_dispatcher)
