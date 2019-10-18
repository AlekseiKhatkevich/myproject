from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from django.db.models import F
from api import models
import uuid
import json
import os
import random


class Command(BaseCommand):

    with open(os.path.join(settings.BASE_DIR, 'data', 'names', 'firstnames_f.json')) as json_file:
        female_names = json.load(json_file)

    with open(os.path.join(settings.BASE_DIR, 'data', 'names', 'firstnames_m.json')) as json_file:
        male_names = json.load(json_file)

    with open(os.path.join(settings.BASE_DIR, 'data', 'names', 'surnames.json')) as json_file:
        surnames = json.load(json_file)

    with open(os.path.join(settings.BASE_DIR, 'data', 'pg1080.txt')) as text_file:
        text_lines = text_file.readlines()

    departments = ['logistic', 'financial', 'accounting', 'warehouse', 'security', 'cooking', 'IT',
                   'HR', 'public relations', 'legal', 'executive', 'development', 'engineering',
                   'testing', 'delivery', 'scientific', 'janitors']

    def genarate_product_data(self):
        data = {
            'name':
                random.choice(random.choice([self.female_names, self.male_names])) + " "
                + random.choice(self.surnames),
            'standard':
                uuid.uuid4().hex[:10].upper().replace('0', 'X').replace('O', 'Y'),
            'weight':
                round(random.uniform(0.1, 300.0), 2),
            'dimensions':
                '%s, %s, %s' %
                (round(random.uniform(50, 2000), 2),
                 round(random.uniform(50, 2000), 2),
                 round(random.uniform(50, 2000), 2)),
            'description': (random.choice(self.text_lines)).strip(),
            'department': random.choice(self.departments),
        }
        return data

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantity',
            default=None,
            required=True,
            type=int,
            help='Quantity of the product to create')

    def handle(self, *args, **options):
        quantity = options.get('quantity', None)

        models.Product.objects.bulk_create(
            (
                models.Product(**self.genarate_product_data()) for i in range(quantity)
            )
        )

        models.Product.objects.all().update(
            textsearchable_index_col=SearchVector(F('description'), config=F('lang'))
        )

