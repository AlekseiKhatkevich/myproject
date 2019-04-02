
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
"""
