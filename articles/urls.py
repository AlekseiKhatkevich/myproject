from django.urls import path
from .views import *

app_name = 'articles'
urlpatterns = [
    path("<int:current_heading_pk>/<int:pk>", ContentListView.as_view(), name="detail"), # new
    path("<int:pk>/", show_by_heading_view, name="show_by_heading"),
    path("", ArticlesMainView.as_view(), name="articles_main"),

]
