from django.urls import path
from .views import *

app_name = 'articles'
urlpatterns = [
    path("<int:pk>/", show_by_heading_view, name="show_by_heading"),
    path("", ArticlesMainView.as_view(), name="articles_main"),

]
