# Generated by Django 2.2.6 on 2019-10-18 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_dog'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Dog',
        ),
        migrations.DeleteModel(
            name='Page',
        ),
        migrations.DeleteModel(
            name='Post',
        ),
    ]
