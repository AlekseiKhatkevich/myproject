# Generated by Django 2.2.1 on 2019-05-22 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0025_auto_20190507_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boatmodel',
            name='first_year',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='first manufacturing year of the model'),
        ),
        migrations.AlterField(
            model_name='boatmodel',
            name='last_year',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Last manufacturing year of the model'),
        ),
    ]
