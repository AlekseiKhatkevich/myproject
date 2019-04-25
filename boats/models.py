from django.db import models
from django.dispatch import Signal
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from .utilities import get_timestamp_path
from easy_thumbnails.fields import  ThumbnailerImageField
from .utilities import *
from django.core.exceptions import ObjectDoesNotExist, EmptyResultSet


"""Сигнал user_registrated
#573  431  437
"""
user_registrated = Signal(providing_args=["instance"])


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notofication(kwargs["instance"])


user_registrated.connect(user_registrated_dispatcher)

""" вторичная модель изображений"""


class BoatImage(models.Model):
    boat_photo = models.ImageField(upload_to=get_timestamp_path, blank=True, verbose_name='Boat photo', )

    boat = models.ForeignKey("BoatModel",  on_delete=models.CASCADE, verbose_name="Boat ForeignKey",
                             null=True)

    class Meta:
        verbose_name = "Boat photo"
        verbose_name_plural = "Boat photos"


""" Первичная модель информации о лодке"""


class BoatModel(models.Model):

    SLOOP = "SL"
    KETCH = "KE"
    YAWL = "YA"
    CAT_KETCH = "CK"

    CHOICES = (
        (None, "Please choose  the rigging type"),
        (SLOOP, "Sloop"),
        (KETCH, "Ketch"),
        (YAWL, "Yawl"),
        (CAT_KETCH, "Cat Ketch"),
    )

    author = models.ForeignKey("ExtraUser", on_delete=models.DO_NOTHING,
                               null=True, blank=True,
                               verbose_name="Author of the entry")

    boat_name = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Boat model",
                                 help_text="Please input boat model")

    boat_length = models.FloatField(null=False, blank=False, verbose_name="Boat water-line length",
                                    help_text="Please input boat water-line length",)

    boat_description = models.TextField(blank=True, verbose_name="Boat description",
                                        help_text="Please describe the boat", )

    boat_mast_type = models.CharField(max_length=10, choices=CHOICES,
                                      verbose_name="Boat rigging type",
                                      help_text="Please input boat rigging type")

    boat_price = models.PositiveIntegerField(verbose_name="price of the boat",
                                                  help_text="Please input boat price", )

    boat_country_of_origin = models.CharField(max_length=20, verbose_name="Boat country of origin",
                                              help_text="Please specify boat's country of origin")

    boat_sailboatdata_link = models.URLField(max_length=100, blank=True,
                                             verbose_name="URL to Sailboatdata",
                                             help_text="Please type in URL to Sailboatdata "
                                                       "page for this boat")

    boat_keel_type = models.CharField(max_length=50, verbose_name="Boat keel type",
                                      help_text="Please specify boat's keel type")

    boat_publish_date = models.DateTimeField(auto_now_add=True)

    boat_primary_photo = models.ImageField(upload_to=get_timestamp_path, blank=True, #"photos/"
                                           verbose_name='Boat primary photo',
                                           help_text="Please attach a primary photo of the boat")
    first_year = models.PositiveSmallIntegerField(blank=True, null=True,
                                                  verbose_name="first manufacturing year")
    last_year = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Last manufacturing year")

    def __str__(self):
        return self.boat_name

    class Meta:
        verbose_name = "Boats primary data"
        verbose_name_plural = "Boats primary data"
        ordering = ["-boat_publish_date"]

    def length_mast_keel(self):  # метод добовляет кастомный атрибут в шаблон {{ current_boat.length_mast_keel }}
        if self.boat_length and self.boat_keel_type and self.boat_mast_type:
            return "length - %d feet, keel type - %s, rigging - %s" % (self.boat_length, self.boat_keel_type,  self.boat_mast_type)

    def delete(self, using=None, keep_parents=False):
        from articles.models import SubHeading, UpperHeading
        for ai in self.boatimage_set.all():  # для правильного србатывания django_cleanup
            ai.delete()
            # очистка всех пустых подкатегорий  в категории "Articles on boats" без статей и без связи с
            # лодкой
            # - условия срабатывания системы очистки:
            # 1 находится в папке Articles on boats
            # 2 нет связи с лодкой
            # 3 нет связанных статей
        try:
            subheadings_query_set = SubHeading.objects.filter(foreignkey_id=UpperHeading.objects.get(
                            name__exact="Articles on boats").pk, one_to_one_to_boat_id__isnull=True)
            for subheading in subheadings_query_set:
                if not subheading.article_set.exists():
                    subheading.delete()
        except EmptyResultSet:
            pass
        try:  # удаление sub категорий   связанных с лодкой при ее удалении
            if not SubHeading.objects.get(one_to_one_to_boat=self).article_set.exists():
                self.heading.delete()  # удаляем, если не содержит статей
        except SubHeading.DoesNotExist or ObjectDoesNotExist:
            pass
        models.Model.delete(self, using=None, keep_parents=False)

    #  создание связанной категории статей при создании лодки

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        from articles.models import SubHeading, UpperHeading
        models.Model.save(self, force_insert=False, force_update=False, using=None,
                          update_fields=None)
        SubHeading.objects.update_or_create(one_to_one_to_boat_id=self.id,
                                foreignkey_id=UpperHeading.objects.get
                                (name__exact="Articles on boats").pk, defaults={"name": self.boat_name})


"""Расширенная модель юзера """


class ExtraUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name="Is user activated?",
                                       help_text="Specifies whether user has been activated or not")
    email = models.EmailField(unique=True, blank=False, verbose_name="user's email",
                              help_text='Please type in your email address')

    class Meta(AbstractUser.Meta):
        unique_together = ("first_name", "last_name", )




