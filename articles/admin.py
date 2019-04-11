from django.contrib import admin
from .models import *
from .forms import *


class SubHeadingInline(admin.TabularInline):
    model = SubHeading


class UpperHeadingAdmin(admin.ModelAdmin):
    exclude = ("foreignkey", )
    inlines = (SubHeadingInline, )


class SubHeadingAdmin(admin.ModelAdmin):
    form = SubHeadingForm


class ArticlesAdmin(admin.ModelAdmin):
    list_display = ("foreignkey_to_subheading", "author", "title", "content",
                    "url_to_article", "created_at", )
    fields = (("foreignkey_to_subheading", "author", ),
              "title", "content", "url_to_article")



admin.site.register(UpperHeading, UpperHeadingAdmin)
admin.site.register(SubHeading)  # + SubHeadingAdmin
admin.site.register(Article, ArticlesAdmin)
