from django.urls import path
from .views import *

app_name = 'boats'
urlpatterns = [

    path('account/password/change', PasswordCorrectionView.as_view(), name="password_change"),
    path("account/profile/registerdone/", RegisterDoneView.as_view(), name="register_is_done"),
    path("accounts/profile/change/", CorrectUserInfoView.as_view(), name="profile_change"),
    path("accounts/profile/add/", AddNewUserView.as_view(), name="add_new_user"), #new
    path("accounts/logout/", AdminLogoutView.as_view(), name="logout"),
    path("accounts/profile/", UserProfileView.as_view(), name='user_profile'),
    path("accounts/login/", AdminLoginView.as_view(), name="login"),
    path("boats/detail/<int:boat_id>/", boat_detail_view, name="boat_detail"),
    path("boats/create/", viewname, name="boat_create"),
    path("boats/", boat_view, name="boats"),
    path("", IndexPageView.as_view(), name="index"),
]
