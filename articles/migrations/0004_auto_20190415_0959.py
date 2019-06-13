# Generated by Django 2.2 on 2019-04-15 06:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_auto_20190409_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='content',
            field=models.TextField(blank=True, help_text='Please briefly describe the article', verbose_name='Description of the article'),
        ),
        migrations.AlterField(
            model_name='article',
            name='foreignkey_to_subheading',
            field=models.ForeignKey(help_text='Please choose subheading', on_delete=django.db.models.deletion.PROTECT, to='articles.SubHeading', verbose_name='Subheading'),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(help_text='Please add a title', max_length=50, verbose_name='Article header'),
        ),
        migrations.AlterField(
            model_name='article',
            name='url_to_article',
            field=models.URLField(help_text='Please insert URL of the article', max_length=100, unique=True, verbose_name='URL to the article'),
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together={('foreignkey_to_subheading', 'title')},
        ),
    ]
