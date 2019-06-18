from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from .models import BoatModel, BoatImage
from reversion.models import Version
from reversion.signals import post_revision_commit
from articles.models import Article, Comment
from .utilities import send_activation_notofication
from django.core.signals import Signal
from django.shortcuts import reverse
from fancy_cache.memory import find_urls


@receiver([post_save, post_delete], sender=BoatModel)
def invalidate_cached_lookup_BoatListView(sender, instance, **kwargs):
    """Инвалидация лукапа 'BoatListView'"""
    cache_key = "BoatListView"
    cache.delete(cache_key)


"""Инвалидация лукапа 'boat_detail_view' (вся пачка хендлеров на 1 вьюху"""


@receiver([post_save, post_delete], sender=BoatModel)
def invalidate_cached_lookup_boat_detail_view_by_BoatModel(sender, instance, **kwargs):
    cache_key = "boat_detail_view" + instance.boat_name
    cache.delete(cache_key)


@receiver([post_save, post_delete], sender=BoatImage)
def invalidate_cached_lookup_boat_detail_view_by_BoatImage(sender, instance, **kwargs):
    try:
        cache_key = "boat_detail_view" + instance.boat.boat_name
        cache.delete(cache_key)
    except AttributeError:
        pass


@receiver([post_save, post_delete], sender=Comment)
def invalidate_cached_lookup_boat_detail_view_by_Comment(sender, instance, **kwargs):
    try:
        cache_key = "boat_detail_view" + instance.foreignkey_to_boat.boat_name
        cache.delete(cache_key)
    except AttributeError:
        pass


@receiver([post_save, post_delete], sender=Article)
def invalidate_cached_lookup_boat_detail_view_by_Article(sender, instance, **kwargs):
    try:
        cache_key = "boat_detail_view" + instance.foreignkey_to_boat.boat_name
        cache.delete(cache_key)
    except AttributeError:
        pass


@receiver(post_revision_commit, sender=Version)
def invalidate_cached_lookup_boat_detail_view_by_Reversion(sender, instance, **kwargs):
    try:
        cache_key = "boat_detail_view" + instance.field_dict["boat_name"]
        cache.delete(cache_key)
    except KeyError:
        pass

"""
@receiver(post_delete, sender=Version)
def invalidate_rollback_cache(sender, instance, **kwargs):
  #Удаление кеша RollbackView при финальном удалении реверсии
    cache_key = make_template_fragment_key('rollback', [instance.id, ])
    cache.delete(cache_key)"""






#  ---------------------------------------------------------------------------------------------------
user_registrated = Signal(providing_args=["instance"])
"""Сигнал user_registrated #573  431  437"""


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notofication(kwargs["instance"])


user_registrated.connect(user_registrated_dispatcher)
