from django.urls import path, include
from rest_framework import routers
from api import views
from rest_framework.urlpatterns import format_suffix_patterns


app_name = 'api'
urlpatterns = [
    path("boats/<int:pk>/highlight/", views.BoatHighlight.as_view(), name='boat-highlight'),
    path("boats/<int:pk>/", views.BoatDetail.as_view(), name="boat-detail"),
    path('boats/', views.BoatsList.as_view(), name="boats-list"),
    path("users/<int:pk>/", views.ExtraUserDetailView.as_view(), name='extrauser-detail'),
    path("users/", views.ExtraUserListView.as_view(), name='extrauser-list'),
    path("", views.api_root, name="api_root"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
