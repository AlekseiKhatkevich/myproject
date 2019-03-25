from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
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
    #boats = BoatModel.objects.all()
    current_boat = BoatModel.objects.get(pk=boat_id)  #  primary
    images = BoatImage.objects.filter(boat=boat_id)  # secondary
    #current_boat.boatimage_set.all
    context = {"images": images, "current_boat": current_boat}
    return render(request, "boat_detail.html", context)


class BoatCreateView(CreateView):
    template_name = "create.html"
