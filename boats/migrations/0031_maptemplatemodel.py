# Generated by Django 2.2.2 on 2019-06-21 17:48

from django.db import migrations, models
import django_boto.s3.storage


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0030_extrauser_change_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapTemplateModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('map_template', models.FileField(storage=django_boto.s3.storage.S3Storage(), upload_to='maps/')),
            ],
        ),
    ]
