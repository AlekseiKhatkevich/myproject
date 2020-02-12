# Generated by Django 2.2.6 on 2019-10-09 15:39

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('standard', models.CharField(max_length=40)),
                ('weight', models.PositiveIntegerField()),
                ('dimensions', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('description', models.TextField()),
            ],
        ),
    ]