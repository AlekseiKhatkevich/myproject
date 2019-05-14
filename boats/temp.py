
"""
@login_required
def viewname_edit(request, pk):
    obj1 = BoatModel.objects.get(pk=pk)
    obj2 = BoatImage.objects.filter(boat_id=pk)
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1", instance=obj1)
        form2 = boat_image_formset(request.POST, request.FILES, prefix="form2", queryset=obj2)
        if form1.is_valid() and form2.is_valid():
            prim = form1.save()
            form2.save(commit=False) #  second =
            for deleted_img in form2.deleted_objects: #  279
                deleted_img.delete()
            for changed_img in form2.changed_objects:
                pass
            for new_img in form2.new_objects:
                new_img.boat = prim
            form2.save()
            #for img in second:
                #img.boat = prim
               # img.save()
            messages.add_message(request, messages.SUCCESS, "You successfully edited boat's data")
            return HttpResponseRedirect(reverse_lazy("boats:boat_detail", args=(pk, )))

        else:
            messages.add_message(request, messages.WARNING, "Forms are not valid. Please check the data")
            context = {"form1": form1, "form2": form2}
            return render(request, "edit_boat.html", context)
    else:
        if request.user == obj1.author:
            form1 = BoatForm(prefix="form1", instance=obj1)
            form2 = boat_image_formset(prefix="form2", queryset=obj2)
            context = {"form1": form1, "form2": form2}
            return render(request, "edit_boat.html", context)
        else:
            messages.add_message(request, messages.WARNING, "You can only change your own entries!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))






# todo формсет
@atomic
@login_required
def viewname(request):
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1")
        form2 = BoatImageForm(request.POST, request.FILES, prefix="form2")
        if form1.is_valid() and form2.is_valid():
            prim = form1.save(commit=False)
            prim.author = request.user
            prim.save()
            second = form2.save(commit=False)
            second.boat = prim
            second.save()
            messages.add_message(request, messages.SUCCESS, "You added a new boat")
            return HttpResponseRedirect(reverse_lazy("boats:boat_detail",
                                                     args=(prim.pk, )))
        else:
            messages.add_message(request, messages.WARNING, "Forms are not valid. Please check the data")
            context = {"form1": form1, "form2": form2}
            return render(request, "create.html", context)
    else:
        form1 = BoatForm(prefix="form1")
        form2 = BoatImageForm(prefix="form2")
        context = {"form1": form1, "form2": form2}
        return render(request, "create.html", context)



 prim = form1.save(commit=False)
            prim.author = request.user
            prim.save()
            second = form2.save(commit=False)  # second =
            for deleted_img in form2.deleted_objects:  # 279
                deleted_img.delete()
            for changed_img in form2.changed_objects:
                changed_img.boat = prim
                changed_img.save()
            for new_img in form2.new_objects:
                new_img.boat = prim
            for img in second:
                img.boat = prim
                img.save()
            form2.save()

rgba(41,41,41,0.75)




@atomic
@login_required
def viewname(request):
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1")
        form2 = boat_image_inline_formset(request.POST, request.FILES, prefix="form2", )
        if form1.is_valid():
            prim = form1.save(commit=False)
            prim.author = request.user
            form1.save()
            form2 = boat_image_inline_formset(request.POST, request.FILES,
                                              prefix="form2", instance=prim)
            if form2.is_valid():
                form2.save()
                messages.add_message(request, messages.SUCCESS, "You added a new boat")
                return HttpResponseRedirect(reverse_lazy("boats:boat_detail",
                                                     args=(prim.pk, )))
        else:
            messages.add_message(request, messages.WARNING,
                                 "Forms are not valid. Please check the data", fail_silently=True)
            context = {"form1": form1, "form2": form2}
            return render(request, "create.html", context)
    else:

        form1 = BoatForm(prefix="form1")
        form2 = boat_image_inline_formset(request.POST or None, request.FILES or None, prefix="form2", )
        context = {"form1": form1, "form2": form2}
        return render(request, "create.html", context)






Рабочая создания лодки. Файлы вторичной модели не сохраняются!!! Динамический формсет
@atomic
@login_required
def viewname(request):

    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1")
        if form1.is_valid():
            prim = form1.save(commit=False)
            prim.author = request.user
            form1.save(commit=False)
            form2 = boat_image_inline_formset(request.POST, request.FILES,
                                              prefix="form2", instance=prim)
            if "add_photo" in request.POST:
                cp = request.POST.copy()
                cp['form2-TOTAL_FORMS'] = int(cp['form2-TOTAL_FORMS']) + 1
                form1 = BoatForm(request.POST, request.FILES, prefix="form1")
                form2 = boat_image_inline_formset(cp, request.FILES,
                                                  prefix="form2", instance=prim)
                context = {"form1": form1, "form2": form2}
                return render(request, "create.html", context)
            elif 'submit' in request.POST:
                if form2.is_valid():
                    form1.save()
                    form2.save()
                    messages.add_message(request, messages.SUCCESS, "You added a new boat")
                    return HttpResponseRedirect(reverse_lazy("boats:boat_detail",
                                                     args=(prim.pk, )))
        else:
            form1 = BoatForm(prefix="form1")
            form2 = boat_image_inline_formset(prefix="form2", )
            context = {"form1": form1, "form2": form2}
            return render(request, "create.html", context)

    else:
        form1 = BoatForm(prefix="form1")
        form2 = boat_image_inline_formset(prefix="form2", )
        context = {"form1": form1, "form2": form2}
        return render(request, "create.html", context)



"""
"""
    from django.contrib import admin
    from .models import *
    from .forms import *
    from reversion.admin import VersionAdmin


    class SubHeadingInline(admin.TabularInline):
        model = SubHeading


    


    class UpperHeadingAdmin(admin.ModelAdmin):
        exclude = ("foreignkey", )
        inlines = (SubHeadingInline, )


    


    class DeletedFilter(admin.SimpleListFilter):
        
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
        fields = (("foreignkey_to_subheading", "author", ),
                  "title", "content", "url_to_article", "show")
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
            
            fields = ["foreignkey_to_subheading", "author",
                  "title", "content", "url_to_article"]
            if obj:
                fields.append("show")
            return fields

    


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


"""
