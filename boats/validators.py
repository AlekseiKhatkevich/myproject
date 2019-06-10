from django.core.exceptions import ValidationError
from articles.models import SubHeading
from .models import BoatModel
from django.conf import settings


class UniqueNameValidator:
    """ проверяет есть ли подкатегории за пределами Articles on boats  с именем как имя  создаваемой/редуктируемой лодки """

    def __call__(self, val):
        if SubHeading.objects.filter(name__iexact=val, foreignkey__name__ne=
        "Articles on boats").exists():
            raise ValidationError("Subheading with this name is already exists. Please choose an "
                                  "alternative name or slightly correct current one", code="unique")


class UniqueSailboatLinkValidator:
    """ проверяет есть ли в БД урл на  sailboatdata совпадающий с заносиммы в базу"""
    def __init__(self, pk=0):
        self.pk = pk

    def __call__(self, val):
        if BoatModel.objects.filter(boat_sailboatdata_link__exact=val).exclude(pk=self.pk).exists() and \
                not settings.DEBUG:
            raise ValidationError('Same link to the  "Sailboatdata" is already exist in'
                                  ' database!', code="unique")

