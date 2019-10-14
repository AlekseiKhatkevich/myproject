from django.db import models
from django.contrib.postgres import fields as postgres_fields
from django.core import validators
from django.contrib.postgres.search import SearchVectorField, SearchVector


class Product(models.Model):
    name = models.CharField(max_length=100)
    standard = models.CharField(max_length=40)
    weight = models.PositiveIntegerField()
    dimensions = models.CharField(
        validators=[validators.validate_comma_separated_integer_list], max_length=30)
    description = models.TextField()
    department = models.CharField(max_length=30)
    textsearchable_index_col = SearchVectorField(
        default=SearchVector('english', models.F('description'))
    )
    lang = models.CharField(max_length=25, default='english')



