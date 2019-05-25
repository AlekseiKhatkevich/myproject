from django.db import models
from django.dispatch import Signal, receiver
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from .utilities import files_list, send_activation_notofication, get_timestamp_path, clean_cache, clean_map
from django.core.exceptions import ObjectDoesNotExist, EmptyResultSet
from django_countries.fields import CountryField
from easy_thumbnails.files import get_thumbnailer
from django.db.models.fields import Field
from .lookups import NotEqual
from myproject.settings import CACHES, MEDIA_ROOT
import os
from datetime import datetime
from django.contrib.postgres.indexes import BrinIndex



#   регистрация кастомного lookup
Field.register_lookup(NotEqual)


user_registrated = Signal(providing_args=["instance"])
"""Сигнал user_registrated #573  431  437"""


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notofication(kwargs["instance"])


user_registrated.connect(user_registrated_dispatcher)


""" вторичная модель изображений"""


class BoatImage(models.Model):

    boat_photo = models.ImageField(upload_to=get_timestamp_path, blank=True,
                                   verbose_name='Boat photo', )
    boat = models.ForeignKey("BoatModel",  on_delete=models.SET_NULL, verbose_name="Boat ForeignKey",
                             null=True)
    memory = models.PositiveSmallIntegerField(blank=True, null=True)

    #  запоминаем значение ФК на случай  срабатывания on_delete = SET_NULL (для последующего
    #  восстановления)
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # удаляем изображения без привязки к лодкам со сроком последнего доступа к файлам более 2
        # месяцев
        useless_old_images = BoatImage.objects.filter(boat_id__isnull=True, memory__isnull=False)
        for image in useless_old_images:
                if datetime.now().timestamp() - os.path.getatime(image.boat_photo.path) > 5184000:
                    image.true_delete(self)  # удаляем по настоящему

        if self.boat and not self.memory:  # сохраняем
            self.memory = self.boat_id
        elif not self.boat and self.memory:  # восстанавливаем
            self.boat_id = self.memory
        elif self.boat and self.memory and self.boat_id != self.memory:  # корректируем на крайняк
            self.memory = self.boat_id

        models.Model.save(self, force_insert=False, force_update=False, using=None,
                          update_fields=None)

    def delete(self, using=None, keep_parents=False):  # удаляем thumbnails ассоциированные
        thumbnailer = get_thumbnailer(self.boat_photo)
        thumbnailer.delete_thumbnails()
        # вместо удаления фоток мы устанавкливаем их ФК в <null>
        self.boat.boatimage_set.remove(self)
        #  models.Model.delete(self, using=None, keep_parents=False)

    def true_delete(self, using=None, keep_parents=False):
        """ Удаляем по настоящему"""
        return models.Model.delete(self, using=None, keep_parents=False)

    def __str__(self):
        return "Boat photo - %s, boat name - %s, boat id - %s  " % \
               (self.boat_photo.name, self.boat.boat_name, self.boat_id)

    def filename(self):
        """метод возвращает имя файла"""
        return os.path.basename(self.boat_photo.name)

    @staticmethod
    def clean_media_root():
        """метод очистки лишних изображений в медиа рут"""
        files_in_db = {image.filename() for image in BoatImage.objects.all().only("boat_photo")}
        useless_files = files_list() - files_in_db
        counter = 0
        for file in useless_files:
            os.remove(os.path.join(MEDIA_ROOT, file))
            counter += 1
        print(counter, "\xa0\\files were removed from MEDIA_ROOT")

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

    boat_name = models.CharField(max_length=20, unique=True, db_index=True, verbose_name="Boat model",
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

    boat_country_of_origin = CountryField(verbose_name="Boat country of origin",
                                          blank_label="Select country of origin",
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
                                           help_text="Please attach a primary photo of the "
                                                     "boat")
    first_year = models.PositiveSmallIntegerField(blank=True, null=True,
                                    verbose_name="first manufacturing year of the model")
    last_year = models.PositiveSmallIntegerField(blank=True, null=True,
                                    verbose_name="Last manufacturing year of the model")

    class Meta:
        verbose_name = "Boats primary data"
        verbose_name_plural = "Boats primary data"
        ordering = ["-boat_publish_date"]
        indexes = (BrinIndex(fields=["boat_publish_date"]),)

    def __str__(self):
        return self.boat_name

    def delete(self, using=None, keep_parents=False):
        import articles.models  # to avoid circular import with articles
        """
            # очистка всех пустых подкатегорий  в категории "Articles on boats" без статей и без 
            связи с
            # лодкой
            # - условия срабатывания системы очистки:
            # 1 находится в папке Articles on boats
            # 2 нет связи с лодкой
            # 3 нет связанных статей 
        """
        try:
            subheadings_query_set = articles.models.SubHeading.objects.filter(
                foreignkey_id=articles.models.UpperHeading.objects.get(
                            name__exact="Articles on boats").pk,
                one_to_one_to_boat_id__isnull=True)
            for subheading in subheadings_query_set:
                if not subheading.article_set.exists():
                    subheading.delete()
        except EmptyResultSet:
            pass
        try:  # удаление sub категорий   связанных с лодкой при ее удалении
            if not articles.models.SubHeading.objects.get(
                    one_to_one_to_boat=self).article_set.exists():
                self.heading.delete()  # удаляем, если не содержит статей
        except articles.models.SubHeading.DoesNotExist or ObjectDoesNotExist:
            pass
        for image in self.boatimage_set.all():  # удаляем ассоциированные тумбнейлы
            thumbnailer = get_thumbnailer(image.boat_photo)
            thumbnailer.delete_thumbnails()
        # удаляем карту, если она есть
        clean_map(pk=self.id)
        models.Model.delete(self, using=None, keep_parents=False)

    #  создание связанной категории статей при создании лодки

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        models.Model.save(self, force_insert=False, force_update=False, using=None,
                          update_fields=None)
        clean_cache(path=CACHES.get("file_resubmit").get("LOCATION"), time_interval=86400)
        # очишаем#  кэш  ресубмита (интервал -сутки)
        import articles.models  # to avoid circular import with articles
        # смотрим есть ли  уже категория статей в "Articles on boats"  с именем создаваемой
        # лодки и
        # без связи с  лодкой . На случае если мы  создаем лодку с именем когда то удаленной
        # лодки.
        try:
            subheading = articles.models.SubHeading.objects.prefetch_related("article_set").get(
                name__iexact=self.boat_name, one_to_one_to_boat_id__isnull=True,
                foreignkey_id=articles.models.UpperHeading.objects.get(name__exact="Articles on"
                                                                                   " boats").pk)
            # есть ли у текущей лодки есть подзаголовок? Т.е мы не создаем лодку а изменяем имя
            # текущей
            # лодки и ее имя совпадает с категорией (смотри описание возле try)
            if articles.models.SubHeading.objects.filter(one_to_one_to_boat_id=self.id).exists():
                # получаем   подзаголовок текущей лодки
                current_subheading = articles.models.SubHeading.objects.prefetch_related(
                    "article_set").get(one_to_one_to_boat_id=self.id)
                # каждуй статью в этом подзаголовке связываем с подзаголовком в TRY:
                for article in current_subheading.article_set.all():
                    article.foreignkey_to_subheading = subheading
                    article.save(update_fields=['foreignkey_to_subheading', ])
                current_subheading.delete()  # удаляем текущий подзаголовок

                # связываем подзаголовок с лодкой. С этого места и ниже идет код для создаваемой с
                # нуля
                # лодки. Выше был для лодки в случае изменения ее имени ( уже сущ. лодки)
            subheading.one_to_one_to_boat = self
            subheading.save(update_fields=['one_to_one_to_boat', ])
            # связываем все статьи с текущей или новой лодкой
            for article in subheading.article_set.all():
                self.article_set.add(article)
                article.save(update_fields=['foreignkey_to_boat', ])
        except articles.models.SubHeading.DoesNotExist:  # если нет, то создаем или обновляем
            # категорию
            # согласно имени лодки
            articles.models.SubHeading.objects.update_or_create(one_to_one_to_boat_id=self.id,                          foreignkey_id=articles.models.UpperHeading.objects.get
                (name__exact="Articles on boats").pk, defaults={"name": self.boat_name})


"""Расширенная модель юзера """


class ExtraUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name="Is user activated?", help_text="Specifies whether user has been activated or not")
    email = models.EmailField(unique=True, blank=False, verbose_name="user's email",
                              help_text='Please type in your email address')

    class Meta(AbstractUser.Meta):
        unique_together = ("first_name", "last_name", )
        indexes = (BrinIndex(fields=["date_joined"]), )






