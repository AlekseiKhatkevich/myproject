# Generated by Django 2.2 on 2019-04-19 11:29

import boats.utilities
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0013_auto_20190418_2054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boatimage',
            name='boat_photo',
            field=models.ImageField(blank=True, help_text='Please attach any photo of the boat', upload_to=boats.utilities.get_timestamp_path, verbose_name='Boat photo'),
        ),
    ]
