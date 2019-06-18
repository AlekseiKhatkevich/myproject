from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist, EmptyResultSet
from boats.models import BoatModel, ExtraUser
from dynamic_validator import ModelFieldRequiredMixin
from captcha.fields import CaptchaField
from django.contrib.postgres.indexes import BrinIndex
import datetime

""" модель группы"""


class Heading(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name='heading '
                                                                                    'title')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Order')
    foreignkey = models.ForeignKey("UpperHeading", on_delete=models.PROTECT, null=True,
                                   blank=True, verbose_name="Upper heading", )
    one_to_one_to_boat = models.OneToOneField(BoatModel, on_delete=models.SET_NULL, null=True,
                                              blank=True, verbose_name="correspondent boat"
                                                                       " for the category", )
    change_date = models.DateTimeField(db_index=True, editable=False, auto_now=True)


""" менеджер ап-группы"""


class UpperHeadingManager(models.Manager):
    def get_queryset(self):
        return models.Manager.get_queryset(self).filter(foreignkey__isnull=True)


"""прокси модель ап-группы"""


class UpperHeading(Heading):
    objects = UpperHeadingManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ("order", "name")
        verbose_name = "Upper heading"
        verbose_name_plural = "Upper headings"


"""менеджер под-группы"""


class SubHeadingManager(models.Manager):
    def get_queryset(self):
        return models.Manager.get_queryset(self).filter(foreignkey__isnull=False)


""" прокси модель под-группы"""


class SubHeading(Heading):
    objects = SubHeadingManager()

    def __str__(self):
        return "%s - %s" % (self.foreignkey.name, self.name)

    class Meta:
        proxy = True
        ordering = ("foreignkey__order", "foreignkey__name", "order", "name")
        verbose_name = "Sub heading"
        verbose_name_plural = "Sub headings"


""" Модель самой статьи"""


# функция для генерации ID суперюзера для подстановки в случае самовыпиливания автора
def superuser():
    try:
        user = ExtraUser.objects.get(is_superuser=True)
    except MultipleObjectsReturned:
        user = ExtraUser.objects.get(is_superuser=True, email="hardcase@inbox.ru")
        return user.id
    except ObjectDoesNotExist or EmptyResultSet:
        return 1
    else:
        return user.id


class ArticleManager(models.Manager):
    """Менеджер прямой связи . Показываем только не удаленные статьи"""
    def get_queryset(self):
        return models.Manager.get_queryset(self).exclude(show=False)


class Article(models.Model):
    # менеджеры прямой связи
    default = models.Manager()  # админ использует первый сверху менеджер
    objects = ArticleManager()

    foreignkey_to_subheading = models.ForeignKey(SubHeading,
                                                on_delete=models.PROTECT, verbose_name="Subheading",                                                    help_text="Please choose subheading")
    foreignkey_to_boat = models.ForeignKey(BoatModel, on_delete=models.SET_NULL,                                  verbose_name="Parent boat for article", help_text="Please choose the boat",
                                           blank=True, null=True)
    title = models.CharField(max_length=50, verbose_name="Article title",
                             help_text="Please add a title")
    content = models.TextField(verbose_name='Description of the article',
                               blank=True, help_text="Please briefly describe the article")
    author = models.ForeignKey(ExtraUser, on_delete=models.SET(superuser))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Published at")
    url_to_article = models.URLField(max_length=100, unique=True, verbose_name="URL to the "
                                        "article",help_text="Please insert URL of the article")
    show = models.BooleanField(default=True, blank=False, null=False, verbose_name="deleted mark",
                               help_text='Marked articles are shown everywhere, unmarked considered '
                                         'as deleted ones')
    change_date = models.DateTimeField(blank=True, null=True, auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return "/articles/%s/%s/" % (self.foreignkey_to_subheading.pk, self.pk)

    def delete(self, using=None, keep_parents=False):
        """усланавливаем show=False , чтобы не отображать статьи на сайте вместо их фактического
         удаления. За фильтрацию статей с show=False отвечает переопределенный менеджер прямой
         связи"""
        self.show = False
        # устанавливаем время удаления для последующего показа в форме восстановления
        self.change_date = datetime.datetime.now()
        self.save(update_fields=["show", "change_date"])

    def true_delete(self, using=None, keep_parents=False):
        """ Удаляем по настоящему"""
        return models.Model.delete(self, using=None, keep_parents=False)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-created_at"]
        unique_together = ("foreignkey_to_subheading", "title")
        indexes = (BrinIndex(fields=["created_at"]), )


""" Модель комментов """


class Comment(ModelFieldRequiredMixin, models.Model):
    foreignkey_to_article = models.ForeignKey(Article, blank=True, null=True,
                                on_delete=models.CASCADE, verbose_name="Article",                                                       help_text='Please choose the article to comment on')
    foreignkey_to_boat = models.ForeignKey(BoatModel, blank=True, null=True,
                                           on_delete=models.CASCADE,verbose_name="Boat",
                                           help_text="Please choose the boat to comment on")
    author = models.CharField(max_length=30, verbose_name="Author",
                              help_text="Please type in your name ")
    content = models.TextField(verbose_name="Comment text", help_text="Please type in comment here")
    is_active = models.BooleanField(default=True, db_index=True,
                                    verbose_name="Published", help_text="publish?")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Publish date")
    change_date = models.DateTimeField(db_index=True, editable=False, auto_now=True)

    REQUIRED_TOGGLE_FIELDS = [["foreignkey_to_article", "foreignkey_to_boat"], ]

    def __str__(self):
        return "%s - %s" % ((self.foreignkey_to_article.title if self.foreignkey_to_article
                             else self.foreignkey_to_boat.boat_name), self.content[: 25])

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-created_at", ]
        indexes = (BrinIndex(fields=["created_at"]),)


