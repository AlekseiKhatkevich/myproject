from django.db import models
from django.contrib.auth.models import AbstractUser

""" модель группы"""


class Heading(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name='heading title')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Order')
    foreignkey = models.ForeignKey("UpperHeading", on_delete=models.PROTECT, null=True, blank=True,
                                      verbose_name="Upper heading")


""" менеджер up группы"""


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


