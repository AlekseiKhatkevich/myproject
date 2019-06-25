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
    show_by_heading_page_url = reverse('articles:show_by_heading', args=(instance.id, ))
    list(find_urls([main_page_url, show_by_heading_page_url], purge=True))


@receiver([post_save, post_delete], sender=Article, dispatch_uid=1)
def invalidate_by_Article_articles_app(sender, instance,  **kwargs):
    show_by_heading_page_url = reverse('articles:show_by_heading',
                                       args=(instance.foreignkey_to_subheading_id,))
    article_content_page_url = reverse("articles:detail",
                                       args=(instance.foreignkey_to_subheading_id, instance.id))
    article_resurrection_url = reverse("articles:resurrection")
    main_page_url = reverse('articles:articles_main')
    urls = [show_by_heading_page_url, article_content_page_url]
    if not instance.show:  # если мы "удаляем статью" то инвалидируем кеш страницы
        # восстановления и главной страницы так как счетчики поменяються
        urls.extend([article_resurrection_url, main_page_url])
    #  В случае создания новой статьи мы должны инвалидировать кеш так как счетчик статей в
    #  субкатегориях измениться.
    if kwargs.get("created"):
        urls.append(main_page_url)
    list(find_urls(urls, purge=True))


@receiver([post_save, post_delete], sender=Comment)
def invalidate_by_Comment(sender, instance, **kwargs):
    urls = []
    try:
        article_content_page_url = reverse("articles:detail", args=(
        instance.foreignkey_to_article.foreignkey_to_subheading_id,
        instance.foreignkey_to_article_id))
        urls.append(article_content_page_url)
    except (NoReverseMatch, AttributeError):
        pass
    list(find_urls(urls, purge=True))


