# Generated by Django 2.2.2 on 2019-06-25 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0020_auto_20190621_1744'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subheading',
            options={'ordering': ('foreignkey__name', 'name'), 'verbose_name': 'Sub heading', 'verbose_name_plural': 'Sub headings'},
        ),
    ]
