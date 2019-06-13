# Generated by Django 2.2 on 2019-04-25 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0018_auto_20190425_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boatmodel',
            name='boat_name',
            field=models.TextField(db_index=True, help_text='Please input boat model', max_length=50, unique=True, verbose_name='Boat model'),
        ),
    ]
