from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from django.contrib.postgres.search import SearchVector
from .decorators import skip_signal


@receiver(post_save, sender=Product)
@skip_signal()
def update_vector(sender, instance, **kwargs):
    if instance.is_description_updated or kwargs['created']:
        instance.textsearchable_index_col = SearchVector('description', config=instance.lang)
        instance.skip_signal = True
        instance.save(update_fields=['textsearchable_index_col', ])

