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


admin.site.register(UpperHeading, UpperHeadingAdmin)
admin.site.register(SubHeading)  # + SubHeadingAdmin
