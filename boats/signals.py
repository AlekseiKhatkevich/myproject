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
from django.urls import NoReverseMatch


@receiver([post_save, post_delete], sender=BoatModel)
def invalidate_by_BoatModel(sender, instance, **kwargs):
        cache_key_0 = "BoatListView"
        cache_key_1 = "boat_detail_view" + instance.boat_name
        cache_key_2 = "Pdf+%s" % instance.pk
        cache.delete_many((cache_key_0, cache_key_1, cache_key_2))
        try:
            pdf_url = reverse('boats:pdf_to_file', args=(instance.pk,))
            list(find_urls([pdf_url], purge=True))
        except NoReverseMatch:
            pass


@receiver([post_save, post_delete], sender=BoatImage)
def invalidate_by_BoatImage(sender, instance, **kwargs):
        cache_key_0 = "boat_detail_view" + str(instance.boat_id)
        cache_key_1 = "Pdf+%s" % instance.boat_id
        cache.delete_many((cache_key_0, cache_key_1))
        try:
            pdf_url = reverse('boats:pdf_to_file', args=(instance.boat_id,))
            list(find_urls([pdf_url], purge=True))
        except NoReverseMatch:
            pass


@receiver([post_save, post_delete], sender=Comment)
def invalidate_by_Comment(sender, instance, **kwargs):
    try:
        cache_key = "boat_detail_view" + instance.foreignkey_to_boat.boat_name
        cache.delete(cache_key)
    except AttributeError:
        pass


@receiver([post_save, post_delete], sender=Article)
def invalidate_by_Article(sender, instance, **kwargs):
    try:
        cache_key = "boat_detail_view" + instance.foreignkey_to_boat.boat_name
        cache.delete(cache_key)
    except AttributeError:
        pass


@receiver(post_revision_commit, sender=Version)
def invalidate_by_Version(sender, instance, **kwargs):
    try:
        cache_key = "boat_detail_view" + instance.field_dict["boat_name"]
        cache.delete(cache_key)
    except KeyError:
        pass


#  ---------------------------------------------------------------------------------------------------
user_registrated = Signal(providing_args=["instance"])
"""Сигнал user_registrated #573  431  437"""


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notofication(kwargs["instance"])


user_registrated.connect(user_registrated_dispatcher)
