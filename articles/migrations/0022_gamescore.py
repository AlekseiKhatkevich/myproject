# Generated by Django 2.2.4 on 2019-08-17 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0021_auto_20190625_2131'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('score', models.IntegerField()),
            ],
        ),
    ]
