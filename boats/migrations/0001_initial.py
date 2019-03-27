# Generated by Django 2.1.7 on 2019-03-26 12:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BoatImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boat_photo', models.ImageField(blank=True, help_text='Please attach any photo of the boat', upload_to='photos/', verbose_name='Boat photo')),
            ],
            options={
                'verbose_name': 'Boat photo',
                'verbose_name_plural': 'Boat photos',
            },
        ),
        migrations.CreateModel(
            name='BoatModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boat_name', models.CharField(db_index=True, help_text='Please input boat model', max_length=50, unique=True, verbose_name='Boat model')),
                ('boat_length', models.FloatField(help_text='Please input boat water-line length', verbose_name='Boat water-line length')),
                ('boat_description', models.TextField(blank=True, help_text='Please describe the boat', verbose_name='Boat description')),
                ('boat_mast_type', models.CharField(choices=[('SL', 'Sloop'), ('KE', 'Ketch'), ('YA', 'Yawl'), ('CK', 'Cat Ketch')], default='SL', help_text='Please input boat rigging type', max_length=10, verbose_name='Boat rigging type')),
                ('boat_price', models.PositiveSmallIntegerField(default=0, help_text='Please input boat price', verbose_name='price for the boat')),
                ('boat_country_of_origin', models.CharField(help_text="Please specify boat's country of origin", max_length=20, verbose_name='Boat country of origin')),
                ('boat_sailboatdata_link', models.URLField(blank=True, help_text='Please type in URL to Sailboatdata page for this boat', max_length=100, verbose_name='URL to Sailboatdata')),
                ('boat_keel_type', models.CharField(help_text="Please specify boat's keel type", max_length=50, verbose_name='Boat keel type')),
                ('boat_publish_date', models.DateTimeField(auto_now_add=True)),
                ('boat_primary_photo', models.ImageField(help_text='Please attach a primary photo of the boat', upload_to='photos/', verbose_name='Boat primary photo')),
            ],
            options={
                'verbose_name': 'Boats primary data',
                'verbose_name_plural': 'Boats primary data',
                'ordering': ['boat_name'],
            },
        ),
        migrations.AddField(
            model_name='boatimage',
            name='boat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boats.BoatModel', verbose_name='Boat ForeignKey'),
        ),
    ]
