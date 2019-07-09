from django.urls import path, include
from rest_framework import routers
from .views import boats_list, boat_detail, BoatDetail, BoatsList
from rest_framework.urlpatterns import format_suffix_patterns


app_name = 'api'
urlpatterns = [
    path("boats/<int:pk>/", BoatDetail.as_view(), name="boat_detail"),
    path('boats/', BoatsList.as_view(), name="boats"),

]

urlpatterns = format_suffix_patterns(urlpatterns)
