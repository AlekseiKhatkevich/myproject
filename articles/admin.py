from django.contrib import admin
from .models import *
from .forms import *
from reversion.admin import VersionAdmin
from django.contrib import messages


def delete_within_deleted_articles(SubHeadingAdmin, request, queryset):
    """Метод удаляет подкатегорию вместе с "удаленными" статьями """
    subheadings_cnt = 0
    articles_cnt = 0
    for subheading in queryset:  # если нет "неудаленных" статей и есть "удаленные":
        if not subheading.article_set(manager="reverse").exists() and \
                subheading.article_set.exists():
            for article in subheading.article_set.all():
                article.true_delete()  # мы удаляем "удаленные статьи"  чтобы on_delete.PROTECT
            # позволил удалить  Subheading
                articles_cnt += 1
                subheading.delete()
                subheadings_cnt += 1
    if subheadings_cnt:  # Если что то удалили...
        if subheadings_cnt == 1:
            message = "Subheading  is deleted within %d articles marked as deleted ones" % \
                      articles_cnt
        else:
            message = "Subheadings  - %d pcs. are deleted within %d articles marked as deleted " \
                          "ones" % (subheadings_cnt, articles_cnt)
    else:  # Если ничего не удалили
        message = "You have non-deleted articles in subheading. Can not delete subheading " \
                  "because of that"
    SubHeadingAdmin.message_user(request, message=message, fail_silently=True)


"""Инлайн подкатегорий"""


class SubHeadingInline(admin.TabularInline):
    model = SubHeading
    show_change_link = True
    admin_caching_enabled = True
    admin_caching_timeout_seconds = 60 * 60 * 24


"""Подкатегории(отдельно, не инлайн)"""


@admin.register(SubHeading)
class SubHeadingAdmin(VersionAdmin):
    admin_caching_enabled = True
    admin_caching_timeout_seconds = 60 * 60 * 24
    actions = [delete_within_deleted_articles, ]


"""ап-категория """


class UpperHeadingAdmin(admin.ModelAdmin):
    exclude = ("foreignkey", )
    inlines = (SubHeadingInline, )
    raw_id_fields = ("one_to_one_to_boat", )
    admin_caching_enabled = True
    admin_caching_timeout_seconds = 60 * 60 * 24


"""статьи"""


def fake_delete(ArticlesAdmin, request, queryset):
    """метод добавляет  в actions select возможность удалять статьи переводом show в False"""
    message = "Articles: "
    for cnt, rec in enumerate(queryset.only("title"), 1):
        rec.delete()
        if cnt != queryset.count():
            message += " " + rec.title + " "
        else:
            message += " " + rec.title + ",  "
    message += " have deleted , totally - %d articles" % queryset.count()
    ArticlesAdmin.message_user(request, message=message, fail_silently=True)


def kinda_undelete(ArticlesAdmin, request, queryset):
    """метод переводит show в True"""
    cnt = queryset.filter(show=False).update(show=True)
    if cnt == 0:
        message, level = "Please select only deleted articles to recover", messages.WARNING
    else:
        message, level = "% d articles have been restored" % cnt, messages.INFO
    ArticlesAdmin.message_user(request, message=message, fail_silently=True, level=level)


fake_delete.short_description = "Mark as deleted instead of TRUE delete"
kinda_undelete.short_description = "Recover deleted articles"


class DeletedFilter(admin.SimpleListFilter):
    """ фильтация и показ удаленных статей в отдельной группе"""
    title = " show deleted articles"
    parameter_name = "mark"

    def lookups(self, request, model_admin):
        return (('deleted', "Deleted Articles"),
                ("intact", "Non deleted articles")
                )

    def queryset(self, request, queryset):
        if self.value() == "deleted":
            return Article.default.filter(show=False)
        elif self.value() == "intact":
            return Article.objects.all()


@admin.register(Article)
class ArticlesAdmin(VersionAdmin):
    list_display = ("foreignkey_to_subheading", "show", "author", "title", "created_at", )
    fields = (("foreignkey_to_subheading", "author"),
              "title",
              "content", "url_to_article", "show")
    list_display_links = ("foreignkey_to_subheading", "title",)
    list_editable = ("show", )
    search_fields = ("^title", "^content")
    list_filter = (DeletedFilter, "foreignkey_to_subheading__foreignkey__name",
                   "foreignkey_to_subheading__name", )
    list_select_related = True
    raw_id_fields = ("foreignkey_to_subheading", "foreignkey_to_boat")
    date_hierarchy = "created_at"
    actions = (fake_delete, kinda_undelete)
    admin_caching_enabled = True
    admin_caching_timeout_seconds = 60 * 60 * 24

    def get_queryset(self, request):
        return VersionAdmin.get_queryset(self, request)

    def get_fields(self, request, obj=None):
        """метод показывает поле "show" только у изменяемых, а не создаваемых записей"""
        fields = ["foreignkey_to_subheading", "author",
                  "title", "content", "url_to_article"]
        if obj:
            fields.insert(5, "show")
        return fields


"""комменты"""


@admin.register(Comment)  # manage.py createinitialrevisions
class CommentAdmin(VersionAdmin):
    list_display = ("__str__", "foreignkey_to_article", "foreignkey_to_boat", "author", "is_active", "created_at")
    list_display_links = ("__str__", )
    search_fields = ("^author", )
    readonly_fields = ("created_at", )
    ordering = ("foreignkey_to_article", "foreignkey_to_boat", "-created_at", )
    list_select_related = True
    admin_caching_enabled = True
    admin_caching_timeout_seconds = 60 * 60 * 24


admin.site.register(UpperHeading, UpperHeadingAdmin)


