# Ha sido  generado  por me mismo en 2019-10-14 15:53

from django.db import migrations
from django.contrib.contenttypes.models import ContentType


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20191013_1553'),
    ]

    try:
        con = ContentType.objects.get_by_natural_key(app_label='api', model='product')
        model = ContentType.model_class(con)
        db_table = model._meta.db_table

        operations = [
            migrations.RunSQL(
                """           
                DROP TRIGGER IF EXISTS text_searchable_update ON api_product  
                """,

                reverse_sql=migrations.RunSQL.noop

                ,
            ),

            migrations.RunSQL(
                """
                CREATE TRIGGER text_searchable_update BEFORE INSERT OR UPDATE
                ON api_product FOR EACH ROW EXECUTE FUNCTION
                tsvector_update_trigger(textsearchable_index_col, 'pg_catalog.english', description)
                """,

                reverse_sql=

                """           
                DROP TRIGGER IF EXISTS text_searchable_update ON api_product  
                """,
            )
        ]
    except ContentType.DoesNotExist:
        operations = []
