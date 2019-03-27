from django.urls import path
from .views import *

urlpatterns = [
    path("", ArticlesMainView.as_view(), name="articles_main"),

]
