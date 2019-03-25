# Generated by Django 2.1.7 on 2019-03-24 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boats', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='boatmodel',
            options={'ordering': ['boat_name'], 'verbose_name': 'Boats primary data', 'verbose_name_plural': 'Boats primary data'},
        ),
        migrations.AlterField(
            model_name='boatmodel',
            name='boat_description',
            field=models.TextField(blank=True, help_text='Please describe the boat', verbose_name='Boat description'),
        ),
        migrations.AlterField(
            model_name='boatmodel',
            name='boat_mast_type',
            field=models.CharField(choices=[('SL', 'Sloop'), ('KE', 'Ketch'), ('YA', 'Yawl'), ('CK', 'Cat Ketch')], default='SL', help_text='Please input boat rigging type', max_length=10, verbose_name='Boat rigging type'),
        ),
        migrations.AlterField(
            model_name='boatmodel',
            name='boat_sailboatdata_link',
            field=models.URLField(blank=True, help_text='Please type in URL to Sailboatdata page for this boat', max_length=100, verbose_name='URL to Sailboatdata'),
        ),
    ]
