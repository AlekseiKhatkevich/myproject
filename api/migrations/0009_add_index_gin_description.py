# Generated by Django 2.2.6 on 2019-10-14 20:18

from django.db import migrations
from django.contrib.contenttypes.models import ContentType
import django.contrib.postgres.indexes


class Migration(migrations.Migration):
    # https://realpython.com/create-django-index-without-downtime/
    atomic = False

    dependencies = [
        ('api', '0008_trigger_999'),
    ]

    try:
        con = ContentType.objects.get_by_natural_key(app_label='api', model='product')

        operations = [
            migrations.SeparateDatabaseAndState(
                state_operations=
                [
                    migrations.AddIndex(
                        model_name='product',
                        index=django.contrib.postgres.indexes.GinIndex(fields=['description'],                              name='decription_fts_gin_idx'),
                    ),
                ],
                database_operations=[
                    migrations.RunSQL(sql=
                        """
                        CREATE INDEX CONCURRENTLY IF NOT EXISTS 
                        decription_fts_gin_idx ON api_product 
                        USING GIN(to_tsvector('english', description))
                        """
                        ,
                        reverse_sql=

                        """
                        DROP INDEX IF EXISTS decription_fts_gin_idx
                        """
            )
        ]
            )
        ]

    except ContentType.DoesNotExist:
        operations = []