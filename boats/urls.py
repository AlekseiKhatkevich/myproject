from django.urls import path
from .views import *

urlpatterns = [

    path("boats/detail/<int:boat_id>/", boat_detail_view, name="boat_detail"),
    path("boats/", boat_view, name="boats"),
    path("", IndexPageView.as_view(), name="index"),
]
