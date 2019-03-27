from django.urls import path
from .views import *

app_name = 'articles'
urlpatterns = [
    path("", ArticlesMainView.as_view(), name="articles_main"),

]
