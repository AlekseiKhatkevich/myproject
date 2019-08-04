from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from api import views


schema_view = get_schema_view(title="Pastebin Api")


router = DefaultRouter()
#router.register('boats', views.BoatviewSet)
#router.register("users", views.ExtraUserViewSet)

urlpatterns = [
    path("schema/", schema_view),
    path("", views.api_root, name="api-root"),
    path("boats/", views.BoatsListView.as_view(), name="boatmodel-list"),
    path("boats/<int:pk>/", views.BoatDetailView.as_view(), name="boatmodel-detail"),
    path("users", views.ExtraUserListView.as_view(), name="extrauser-list"),
    path("users/<int:pk>/", views.ExtraUserDetailView.as_view(), name="extrauser-detail"),
    path("users/registration/", views.UserRegistrationView.as_view(), name="user-registration"),
    path("users/profile/<int:pk>/", views.UserProfileView.as_view(), name="user-profile"),

]



