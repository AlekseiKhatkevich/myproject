from django.contrib import admin
from .models import *
from .forms import *
from reversion.admin import VersionAdmin


class SubHeadingInline(admin.TabularInline):
    model = SubHeading


class UpperHeadingAdmin(admin.ModelAdmin):
    exclude = ("foreignkey", )
    inlines = (SubHeadingInline, )

"""
class SubHeadingAdmin(admin.ModelAdmin):
    form = SubHeadingForm
"""


@admin.register(Article)
class ArticlesAdmin(VersionAdmin):
    list_display = ("foreignkey_to_subheading", "author", "title", "content",
                    "url_to_article", "created_at", )
    fields = (("foreignkey_to_subheading", "author", ),
              "title", "content", "url_to_article")


admin.site.register(UpperHeading, UpperHeadingAdmin)
admin.site.register(SubHeading)  # + SubHeadingAdmin

