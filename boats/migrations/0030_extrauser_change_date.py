# Generated by Django 2.2.2 on 2019-06-17 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0029_boatmodel_change_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='extrauser',
            name='change_date',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]