# Generated by Django 2.2 on 2019-04-23 06:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0010_auto_20190423_0950'),
    ]

    operations = [
        migrations.RenameField(
            model_name='heading',
            old_name='foreignkey_to_boat',
            new_name='one_to_one_to_boat',
        ),
    ]
