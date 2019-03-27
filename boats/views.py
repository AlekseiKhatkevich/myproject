from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import *
from .forms import *


class IndexPageView(TemplateView):
    template_name = "index.html"


def boat_view(request):
    boats = BoatModel.objects.all()
    images = BoatImage.objects.all()
    context = {"boats": boats, "images": images}
    return render(request, "boats.html", context)


def boat_detail_view(request, boat_id):
    current_boat = BoatModel.objects.get(pk=boat_id)  #  primary
    images = current_boat.boatimage_set.all()
    context = {"images": images, "current_boat": current_boat}
    return render(request, "boat_detail.html", context)


# не используетя
class BoatCreateView(CreateView):
    template_name = "create.html"
    form_class = BoatForm
    success_url = reverse_lazy("boats")

    def get_context_data(self, **kwargs):
        context = CreateView.get_context_data(self, **kwargs)
        context["images"] = BoatImage.objects.all()
        return context


def viewname(request):
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1")
        form2 = BoatImageForm(request.POST, request.FILES, prefix="form2")
        if form1.is_valid() and form2.is_valid():
            BoatModel = form1.save()
            BoatImage = form2.save(commit=False)
            BoatImage.boat = BoatModel
            BoatImage.save()
            return redirect(reverse_lazy("boats"))
    else:
        form1 = BoatForm(prefix="form1")
        form2 = BoatImageForm(prefix="form2")
        context = {"form1": form1, "form2": form2}
        return render(request, "create.html", context)
