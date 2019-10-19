from django.db import models, connection
from django.db.models import Func, F
from django.core.exceptions import ValidationError
from django.contrib.postgres import fields as postgres_fields
from django.core import validators
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres import indexes as postgres_indexes
from django.forms.models import model_to_dict
import more_itertools


class Product(models.Model):
    name = models.CharField(max_length=100)
    standard = models.CharField(max_length=40)
    weight = models.PositiveIntegerField()
    dimensions = models.CharField(
        validators=[validators.validate_comma_separated_integer_list], max_length=30)
    description = models.TextField()
    department = models.CharField(max_length=30)
    textsearchable_index_col = SearchVectorField()
    lang = models.CharField(max_length=25, default='english')

    class Meta:
        indexes = (postgres_indexes.GinIndex(fields=["description"], name='decription_fts_gin_idx'),)

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        self.__state = model_to_dict(self, fields=['description', 'lang'])

    @property
    def is_description_updated(self):
        __new_state = model_to_dict(self, fields=['description', 'lang'])
        __is_updated = self.__state != __new_state
        self.__state = __new_state
        return __is_updated

    @staticmethod
    def get_list_of_analyzers():
        with connection.cursor() as cursor:
            cursor.execute("""SELECT cfgname FROM pg_ts_config;""")
            list_of_analyzers = [
                'List of available analyzers',
                [more_itertools.one(analyzer) for analyzer in cursor.fetchall()]
            ]
            return list_of_analyzers

    def validate_analyzers(self):
        list_of_analyzers = self.get_list_of_analyzers()
        if list_of_analyzers and (self.lang not in list_of_analyzers[1]):
            raise ValidationError(
                message='Analyzer "%s" not in list of supported analyzers %s' %
                        (self.lang, list_of_analyzers[1])
            )
        return None

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.validate_analyzers()
        models.Model.save(self, force_insert=False, force_update=False, using=None,
                          update_fields=None)


class UniqueWordsTriGramm(models.Model):
    word = models.TextField(primary_key=True)

    def __str__(self):
        return self.word

    class Meta:
        indexes = (postgres_indexes.GinIndex(
            fields=["word"],
            name='words_idx',
            fastupdate=False),
        )

    @classmethod
    def populate(cls):
        # get list of unique words
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT word FROM ts_stat(
                'SELECT to_tsvector(''simple'', description)
                FROM api_product');
                """,
                #[source, ]
            )
            words_in_product_model = frozenset(
                more_itertools.one(word) for word in cursor.fetchall()
                                               )
        #  words in this model
        existing_words_trigram_holder = frozenset(
            word for word in cls.objects.all().values_list('word', flat=True)
        )
        # delete stale words
        words_to_delete = existing_words_trigram_holder.difference(words_in_product_model)

        cls.objects.filter(word__in=words_to_delete).delete()
        # add new words
        words_to_add = words_in_product_model.difference(existing_words_trigram_holder)

        cls.objects.bulk_create(
            [cls(word=word) for word in words_to_add]
        )
        return 'Added %d new words, deleted %d old ones' % \
               (len(words_to_add), len(words_to_delete))

#SELECT * FROM api_uniquewordstrigramm WHERE word %>> 'acce';
