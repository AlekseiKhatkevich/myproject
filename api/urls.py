from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework.authtoken import views as authtoken_views
from api import views


schema_view = get_schema_view(title="Pastebin Api")


router = DefaultRouter()

urlpatterns = [
    path('api-token-auth/', authtoken_views.obtain_auth_token, name="obtain-token"),
    path("schema/", schema_view, name="schema"),
    path("boats/<int:pk>/", views.BoatDetailView.as_view(), name="boatmodel-detail"),
    path("boats/", views.BoatsListView.as_view(), name="boatmodel-list"),
    path("users/login/", views.UserLoginView.as_view(), name="login"),
    path("users/registration/", views.UserRegistrationView.as_view(), name="user-registration"),
    path("users/profile/", views.UserProfileView.as_view(), name="user-profile"),
    path("users/<int:pk>/", views.ExtraUserDetailView.as_view(), name="extrauser-detail"),
    path("users", views.ExtraUserListView.as_view(), name="extrauser-list"),
    path("product/search/", views.ProductSearchListView.as_view(), name="product-search"),
    path("product/suggest/<str:word>/", views.SuggestionView.as_view(), name="product-suggest"),
    path("", views.api_root, name="api-root"),

]



