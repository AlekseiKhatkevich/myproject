from django.core.exceptions import ValidationError
from articles.models import SubHeading
from .models import BoatModel
from myproject.settings import DEBUG

""" проверяет есть ли подкатегории за пределами Articles on boats  с именем как имя  создаваемой/редуктируемой лодки """


class UniqueNameValidator:

    def __call__(self, val):
        if SubHeading.objects.filter(name__iexact=val, foreignkey__name__ne="Articles on boats").exists():
        #if SubHeading.objects.filter(name__iexact=val).exclude(foreignkey__name="Articles on boats").
        # exists():
            raise ValidationError("Subheading with this name is already exists", code="unique")


""" проверяет есть ли в БД урл на  sailboatdata совпадающий с заносиммы в базу"""


class UniqueSailboatLinkValidator:

    def __call__(self, val):
        if BoatModel.objects.filter(boat_sailboatdata_link__exact=val).exists() and not DEBUG:
            raise ValidationError('same link to the  "Sailboatdata" is already exist in database!',
                                  code="unique")

