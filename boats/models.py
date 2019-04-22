from django.db import models
from django.dispatch import Signal
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from .utilities import get_timestamp_path
from easy_thumbnails.fields import  ThumbnailerImageField
from .utilities import *
from django.core.exceptions import ObjectDoesNotExist


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
        for ai in self.boatimage_set.all():  # для правильного србатывания django_cleanup
            ai.delete()

        try:  # удаление категории статей  связанных с лодкой при ее удалении
            from articles.models import SubHeading, UpperHeading
            boat_related_subheading = SubHeading.objects.get(name__exact=self.boat_name,
                                   foreignkey_id=UpperHeading.objects.get
                                   (name__exact="Articles on boats").pk)
            if not boat_related_subheading.article_set.exists():
                # если категория пустая(без статей) - то удаляем ее
                boat_related_subheading.delete()
        except ObjectDoesNotExist:
            pass
        models.Model.delete(self, using=None, keep_parents=False)

    #  создание связанной категории статей при создании лодки

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        from articles.models import SubHeading, UpperHeading
        upper_heading = UpperHeading.objects.get(name__exact="Articles on boats")
        SubHeading.objects.update_or_create(name=self.boat_name, order=0,
                                            foreignkey_id=upper_heading.pk)
                                            """
        from articles.models import SubHeading, UpperHeading
        SubHeading.objects.update_or_create(foreignkey_to_boat_id=self.id)
        self.subheading_set.update_or_create(name=self.boat_name, order=0, )
        models.Model.save(self, force_insert=False, force_update=False, using=None,
                          update_fields=None)


"""Расширенная модель юзера """


class ExtraUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name="Is user activated?",
                                       help_text="Specifies whether user has been activated or not")
    email = models.EmailField(unique=True, blank=False, verbose_name="user's email",
                              help_text='please type in your email address')  # new

    class Meta(AbstractUser.Meta):
        unique_together = ("first_name", "last_name", )




