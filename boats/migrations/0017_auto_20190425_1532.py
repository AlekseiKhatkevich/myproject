# Generated by Django 2.2 on 2019-04-25 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0016_auto_20190422_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extrauser',
            name='email',
            field=models.EmailField(help_text='Please type in your email address', max_length=254, unique=True, verbose_name="user's email"),
        ),
    ]
