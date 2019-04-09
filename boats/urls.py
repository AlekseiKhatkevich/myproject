from django.urls import path
from .views import *

app_name = 'boats'
urlpatterns = [
    path("test/", TestView.as_view(), name="test"),
    path("accounts/reset/<uidb64>/<token>/", PassResConfView.as_view(), name='password_reset_confirm'),
    path("accounts/password_reset/", PassResView.as_view(), name="password_reset"),
    path("accounts/register/activate/<str:sign>/", user_activate_view, name="register_activate"),
    path('account/password/change', PasswordCorrectionView.as_view(), name="password_change"),
    path("account/profile/registerdone/", RegisterDoneView.as_view(), name="register_is_done"),
    path("accounts/profile/delete/", DeleteUserView.as_view(), name="profile_delete"),
    path("accounts/profile/change/", CorrectUserInfoView.as_view(), name="profile_change"),
    path("accounts/profile/add/", AddNewUserView.as_view(), name="add_new_user"),
    path("accounts/logout/", AdminLogoutView.as_view(), name="logout"),
    path("accounts/profile/", UserProfileView.as_view(), name='user_profile'),
    path("accounts/login/", AdminLoginView.as_view(), name="login"),
    path("boats/edit/<int:pk>/", viewname_edit, name="boat_edit"),
    path("boats/detail/<int:pk>/", boat_detail_view, name="boat_detail"),
    path("boats/delete/<int:pk>/", BoatDeleteView.as_view(), name="boat_delete"),
    path("boats/create/", CreateBoatView.as_view(), name="boat_create"),
    path("boats/", boat_view, name="boats"),
    path("feedback/", feedback_view, name="feedback"),
    path("", IndexPageView.as_view(), name="index"),
]
