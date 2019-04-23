# Generated by Django 2.2 on 2019-04-22 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0015_auto_20190422_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boatmodel',
            name='boat_mast_type',
            field=models.CharField(choices=[(None, 'Please choose  the rigging type'), ('SL', 'Sloop'), ('KE', 'Ketch'), ('YA', 'Yawl'), ('CK', 'Cat Ketch')], help_text='Please input boat rigging type', max_length=10, verbose_name='Boat rigging type'),
        ),
    ]
