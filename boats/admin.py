from django.contrib import admin
from .models import *
from reversion.admin import VersionAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from file_resubmit.admin import AdminResubmitMixin
""" Инлайн вторичной модели изображений для админа лодок"""


class BoatimageInline(admin.TabularInline):
    model = BoatImage
    readonly_fields = ["boat_image", ]

    @staticmethod
    def boat_image(obj):  # выводит миниатюры в админке http://books.agiliq.com/projects/django-admin-cookbook/en/latest/imagefield.html
        try:
            return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
                url=obj.boat_photo.url,
                width=obj.boat_photo.width,
                height=obj.boat_photo.height, ))
        except FileNotFoundError:
            return mark_safe("File Not Found")


""" админ  основной модели лодок"""


@admin.register(BoatModel)
class BoatsAdmin( VersionAdmin):
    list_display = ("boat_name", "boat_length", "boat_mast_type", "boat_keel_type", "boat_primary_photo", "author")
    list_display_links = ("boat_name",)
    search_fields = ("boat_name",)
    inlines = (BoatimageInline, )


""" админ дополнительной (расширенной) модели пользователя"""


@admin.register(ExtraUser)
class ExtraUserAdmin(VersionAdmin): # VersionAdmin reversion app восстановление удаленных данных
    list_display = ("__str__", "is_activated", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    fields = (("username", "email"), ("first_name", 'last_name'),
              ("password",),
              ("is_active", "is_activated"),
              ("is_staff", "is_superuser"),
              ("groups", "user_permissions"),
              ("last_login", "date_joined"),
              )
    readonly_fields = ("last_login",)

