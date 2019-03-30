from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


class BoatimageInline(admin.TabularInline):
    model = BoatImage


class BoatsAdmin(admin.ModelAdmin):
    list_display = ("boat_name", "boat_length", "boat_mast_type", "boat_keel_type", "boat_primary_photo", "author")  #  new
    list_display_links = ("boat_name",)
    search_fields = ("boat_name",)
    inlines = (BoatimageInline, )


admin.site.register(BoatModel, BoatsAdmin)
#admin.site.register(BoatImage, )
admin.site.register(ExtraUser, )
