from django.urls import path
from .views import *

app_name = 'articles'
urlpatterns = [
    path("<int:current_heading_pk>/<int:pk>", ContentListView.as_view(), name="detail"),
    path("<int:pk>/", show_by_heading_view, name="show_by_heading"),
    path("article_delete/<int:pk>/", ArticleDeleteView.as_view(), name="article_delete"),
    path("article_edit/<int:pk>/", ArticleEditView.as_view(), name="article_edit"),
    path("add_article/<int:pk>/", AddArticleView.as_view(), name="add_article"),
    path("", ArticlesMainView.as_view(), name="articles_main"),

]
