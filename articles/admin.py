from django.contrib import admin
from .models import *
from .forms import *
from reversion.admin import VersionAdmin


class SubHeadingInline(admin.TabularInline):
    model = SubHeading


"""ап-категория """


class UpperHeadingAdmin(admin.ModelAdmin):
    exclude = ("foreignkey", )
    inlines = (SubHeadingInline, )


"""статьи"""


@admin.register(Article)
class ArticlesAdmin(VersionAdmin):
    list_display = ("foreignkey_to_subheading", "author", "title", "content",
                    "url_to_article", "created_at", )
    fields = (("foreignkey_to_subheading", "author", ),
              "title", "content", "url_to_article")


"""комменты"""


@admin.register(Comment) # manage.py createinitialrevisions
class CommentAdmin(VersionAdmin):
    list_display = ("__str__", "foreignkey_to_article", "foreignkey_to_boat", "author", "is_active", "created_at")
    list_display_links = ("__str__", )
    search_fields = ("author", )
    readonly_fields = ("created_at", )
    ordering = ("foreignkey_to_article", "foreignkey_to_boat", "-created_at", )


admin.site.register(UpperHeading, UpperHeadingAdmin)
admin.site.register(SubHeading)

