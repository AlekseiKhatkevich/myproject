# Generated by Django 2.2.1 on 2019-05-30 15:36

import boats.utilities
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0026_auto_20190522_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boatimage',
            name='boat_photo',
            field=models.ImageField(blank=True, null=True, upload_to=boats.utilities.get_timestamp_path, verbose_name='Boat photo'),
        ),
    ]
