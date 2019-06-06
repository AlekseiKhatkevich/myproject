# Generated by Django 2.1.7 on 2019-03-30 09:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0003_auto_20190329_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='boatmodel',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Author of the entry'),
        ),
    ]