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
    list_filter = (DeletedFilter, "foreignkey_to_subheading", )
    list_select_related = True
    raw_id_fields = ("foreignkey_to_subheading", "foreignkey_to_boat")
    date_hierarchy = "created_at"

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


admin.site.register(UpperHeading, UpperHeadingAdmin)
admin.site.register(SubHeading)

