from django.contrib import admin
from .models import *
from reversion.admin import VersionAdmin
from django.utils.safestring import mark_safe
from .forms import BoatForm
from .widgets import CustomKeepImageWidget

""" Инлайн вторичной модели изображений для админа лодок"""


class BoatimageInline(admin.TabularInline):
    model = BoatImage
    readonly_fields = ["boat_image", "memory"]
    formfield_overrides = {models.ImageField: {"widget": CustomKeepImageWidget}}
    admin_caching_enabled = True
    admin_caching_timeout_seconds = 60 * 60 * 24

    @staticmethod
    def boat_image(obj):  # выводит миниатюры в админке http://books.agiliq.com/projects/django-admin-cookbook/en/latest/imagefield.html
        try:
            return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
                url=obj.boat_photo.url,
                width=obj.boat_photo.width,
                height=obj.boat_photo.height, ))
        except FileNotFoundError:
            return mark_safe("File Not Found")


""" Инлайн модели шаблонов карт лодки"""


class MapTemplateModelInline(admin.TabularInline):
    model = MapTemplateModel


""" админ  основной модели лодок"""


@admin.register(BoatModel)
class BoatsAdmin(VersionAdmin):
    list_display = ("boat_name", "boat_length", "boat_mast_type", "boat_keel_type", "author")
    list_display_links = ("boat_name",)
    search_fields = ("boat_name",)
    inlines = (BoatimageInline, MapTemplateModelInline)
    list_select_related = True
    radio_fields = {"author": admin.HORIZONTAL}
    form = BoatForm
    admin_caching_enabled = True
    admin_caching_timeout_seconds = 60*60*24

    def get_fields(self, request, obj=None):
        """Показываем поле currency только для создаваемой модели"""
        fields = list(super(BoatsAdmin, self).get_fields(request, obj))
        exclude_set = set()
        if obj:  # obj will be None on the add page, and something on change pages
            exclude_set.add('currency')
        return [f for f in fields if f not in exclude_set]


""" админ дополнительной (расширенной) модели пользователя"""


@admin.register(ExtraUser)
class ExtraUserAdmin(VersionAdmin):  # VersionAdmin reversion app восстановление удаленных данных
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
    list_select_related = True
    admin_caching_enabled = True
    admin_caching_timeout_seconds = 60 * 60 * 24


