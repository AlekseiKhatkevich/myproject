# Generated by Django 2.2 on 2019-04-12 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0007_auto_20190412_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boatmodel',
            name='boat_price',
            field=models.PositiveIntegerField(help_text='Please input boat price', verbose_name='price of the boat'),
        ),
    ]