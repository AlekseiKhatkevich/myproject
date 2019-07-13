from django.urls import path, include
from rest_framework import routers
from api import views
from rest_framework.urlpatterns import format_suffix_patterns


app_name = 'api'
urlpatterns = [
    path("boats/<int:pk>/", views.BoatDetail.as_view(), name="boat_detail"),
    path('boats/', views.BoatsList.as_view(), name="boats"),
    path("users/<int:pk>/", views.ExtraUserDetailView.as_view(), name='extrauser_list'),
    path("users/", views.ExtraUserListView.as_view(), name='extrauser_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
