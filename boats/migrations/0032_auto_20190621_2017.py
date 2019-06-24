# Generated by Django 2.2.2 on 2019-06-21 20:17

from django.db import migrations, models
import django_boto.s3.storage


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0031_maptemplatemodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='maptemplatemodel',
            name='boat_id',
            field=models.PositiveSmallIntegerField(default=1, unique=True, verbose_name='id of the boat'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='maptemplatemodel',
            name='map_template',
            field=models.FileField(storage=django_boto.s3.storage.S3Storage(), unique=True, upload_to='maps/', verbose_name='map template'),
        ),
    ]