from django.contrib import admin
from .models import *


class SubHeadingInline(admin.TabularInline):
    model = SubHeading


class UpperHeadingAdmin(admin.ModelAdmin):
    exclude = ("foreignkey", )
    inlines = (SubHeadingInline, )


admin.site.register(UpperHeading, UpperHeadingAdmin)

