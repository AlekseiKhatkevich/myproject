# Generated by Django 2.2.6 on 2019-10-16 20:52

from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20191016_2021'),
    ]

    operations = [
        UnaccentExtension(), TrigramExtension(),
    ]