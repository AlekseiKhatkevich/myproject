# Generated by Django 2.2.2 on 2019-06-12 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0017_auto_20190517_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='change_date',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AddField(
            model_name='heading',
            name='change_date',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(help_text='Please add a title', max_length=50, verbose_name='Article title'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.CharField(help_text='Please type in your name ', max_length=30, verbose_name='Author'),
        ),
    ]
