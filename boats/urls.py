from django.urls import path
from .views import *

app_name = 'boats'
urlpatterns = [
    path("accounts/profile/", UserProfileView.as_view(), name='user_profile'),
    path("accounts/login/", AdminLoginView.as_view(), name="login"),
    path("boats/detail/<int:boat_id>/", boat_detail_view, name="boat_detail"),
    path("boats/create/", viewname, name="boat_create"),
    path("boats/", boat_view, name="boats"),
    path("", IndexPageView.as_view(), name="index"),
]
