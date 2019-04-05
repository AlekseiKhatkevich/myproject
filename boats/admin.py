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


class ExtraUserAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_activated", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    fields = (("username", "email"), ("first_name", 'last_name'),
              ("is_active", "is_activated"),
              ("is_staff", "is_superuser"),
              ("groups", "user_permissions"),
              ("last_login", "date_joined"))
    readonly_fields = ("last_login", "date_joined")


admin.site.register(BoatModel, BoatsAdmin)
admin.site.register(ExtraUser, ExtraUserAdmin)
