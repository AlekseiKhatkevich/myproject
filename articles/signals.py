from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from .models import Article, Heading, SubHeading, Comment, UpperHeading
from django.shortcuts import reverse
from fancy_cache.memory import find_urls
from django.urls import NoReverseMatch


@receiver([post_save, post_delete], sender=UpperHeading)
def invalidate_by_UpperHeading(sender, instance, **kwargs):
        main_page_url = reverse('articles:articles_main')
        list(find_urls([main_page_url], purge=True))


@receiver([post_save, post_delete], sender=SubHeading)
def invalidate_by_Subheading(sender, instance, **kwargs):
    main_page_url = reverse('articles:articles_main')
    show_by_heading_page_url = reverse('articles:show_by_heading',args=(instance.id, ))
    list(find_urls([main_page_url, show_by_heading_page_url], purge=True))


@receiver([post_save, post_delete], sender=Article)
def invalidate_by_Article(sender, instance, update_fields, **kwargs):
    show_by_heading_page_url = reverse('articles:show_by_heading',
                                       args=(instance.foreignkey_to_subheading_id,))
    article_content_page_url = reverse("articles:detail",
                                       args=(instance.foreignkey_to_subheading_id, instance.id))
    article_resurrection_url = reverse("articles:resurrection")
    urls = [show_by_heading_page_url, article_content_page_url]
    if instance.show == False :  # если мы "удаляем статью" то инвалидируем кеш страницы
        # восстановления
        urls.append(article_resurrection_url)
    list(find_urls(urls, purge=True))

"""
@receiver(pre_save, sender=Article)
def invalidate_by_Article_v_pre_save(sender, instance, **kwargs):
   
    article_resurrection_url = reverse("articles:resurrection")
    if instance.show == False:
        list(find_urls([article_resurrection_url], purge=True))"""


@receiver([post_save, post_delete], sender=Comment)
def invalidate_by_Comment(sender, instance, **kwargs):
    try:
        article_content_page_url = reverse("articles:detail", args=(
        instance.foreignkey_to_article.foreignkey_to_subheading_id,
        instance.foreignkey_to_article_id))
    except NoReverseMatch:
        article_content_page_url = None
    list(find_urls([article_content_page_url], purge=True))


