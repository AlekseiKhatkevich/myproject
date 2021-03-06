# Generated by Django 2.2.1 on 2019-05-07 19:37

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0024_auto_20190430_1036'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='boatmodel',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['boat_publish_date'], name='boats_boatm_boat_pu_924ae6_brin'),
        ),
        migrations.AddIndex(
            model_name='extrauser',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['date_joined'], name='boats_extra_date_jo_e3c7f2_brin'),
        ),
    ]
