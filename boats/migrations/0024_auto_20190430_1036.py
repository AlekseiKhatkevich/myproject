# Generated by Django 2.2 on 2019-04-30 07:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0023_auto_20190430_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='boatimage',
            name='memory',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='boatimage',
            name='boat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='boats.BoatModel', verbose_name='Boat ForeignKey'),
        ),
    ]