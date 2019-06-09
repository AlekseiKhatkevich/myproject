# Generated by Django 2.2.2 on 2019-06-08 17:24

import boats.utilities
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields


class Migration(migrations.Migration):

    replaces = [('boats', '0001_initial'), ('boats', '0002_auto_20190329_1403'), ('boats', '0003_auto_20190329_1448'), ('boats', '0004_boatmodel_author'), ('boats', '0005_auto_20190410_1013'), ('boats', '0006_auto_20190410_1726'), ('boats', '0007_auto_20190412_1427'), ('boats', '0008_auto_20190412_1430'), ('boats', '0009_auto_20190412_2223'), ('boats', '0010_auto_20190413_0833'), ('boats', '0011_auto_20190415_0959'), ('boats', '0012_auto_20190416_1721'), ('boats', '0013_auto_20190418_2054'), ('boats', '0014_auto_20190419_1429'), ('boats', '0015_auto_20190422_1058'), ('boats', '0016_auto_20190422_1539'), ('boats', '0017_auto_20190425_1532'), ('boats', '0018_auto_20190425_1726'), ('boats', '0019_auto_20190425_2045'), ('boats', '0020_remove_boatmodel_boat_name'), ('boats', '0021_boatmodel_boat_name'), ('boats', '0022_auto_20190429_1245'), ('boats', '0023_auto_20190430_1035'), ('boats', '0024_auto_20190430_1036'), ('boats', '0025_auto_20190507_2237')]

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(help_text='Please type in your email address', max_length=254, unique=True, verbose_name="user's email")),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_activated', models.BooleanField(db_index=True, default=True, help_text='Specifies whether user has been activated or not', verbose_name='Is user activated?')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
                'unique_together': {('first_name', 'last_name')},
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BoatModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boat_length', models.FloatField(help_text='Please input boat water-line length', verbose_name='Boat water-line length')),
                ('boat_description', models.TextField(blank=True, help_text='Please describe the boat', verbose_name='Boat description')),
                ('boat_mast_type', models.CharField(choices=[(None, 'Please choose  the rigging type'), ('SL', 'Sloop'), ('KE', 'Ketch'), ('YA', 'Yawl'), ('CK', 'Cat Ketch')], help_text='Please input boat rigging type', max_length=10, verbose_name='Boat rigging type')),
                ('boat_price', models.PositiveIntegerField(help_text='Please input boat price', verbose_name='price of the boat')),
                ('boat_country_of_origin', django_countries.fields.CountryField(help_text="Please specify boat's country of origin", max_length=2, verbose_name='Boat country of origin')),
                ('boat_sailboatdata_link', models.URLField(blank=True, help_text='Please type in URL to Sailboatdata page for this boat', max_length=100, verbose_name='URL to Sailboatdata')),
                ('boat_keel_type', models.CharField(help_text="Please specify boat's keel type", max_length=50, verbose_name='Boat keel type')),
                ('boat_publish_date', models.DateTimeField(auto_now_add=True)),
                ('boat_primary_photo', models.ImageField(blank=True, help_text='Please attach a primary photo of the boat', upload_to=boats.utilities.get_timestamp_path, verbose_name='Boat primary photo')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Author of the entry')),
                ('first_year', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='first manufacturing year')),
                ('last_year', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Last manufacturing year')),
                ('boat_name', models.CharField(db_index=True, default=1, help_text='Please input boat model', max_length=20, unique=True, verbose_name='Boat model')),
            ],
            options={
                'verbose_name': 'Boats primary data',
                'verbose_name_plural': 'Boats primary data',
                'ordering': ['-boat_publish_date'],
            },
        ),
        migrations.CreateModel(
            name='BoatImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boat_photo', models.ImageField(blank=True, upload_to=boats.utilities.get_timestamp_path, verbose_name='Boat photo')),
                ('boat', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='boats.BoatModel', verbose_name='Boat ForeignKey')),
                ('memory', models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Boat photo',
                'verbose_name_plural': 'Boat photos',
            },
        ),
        migrations.AddIndex(
            model_name='boatmodel',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['boat_publish_date'], name='boats_boatm_boat_pu_924ae6_brin'),
        ),
        migrations.AddIndex(
            model_name='extrauser',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['date_joined'], name='boats_extra_date_jo_e3c7f2_brin'),
        ),
    ]
