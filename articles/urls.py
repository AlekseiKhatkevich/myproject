from django.urls import path
from .views import *

app_name = 'articles'
urlpatterns = [
    path("<int:current_heading_pk>/<int:pk>/", ContentListView.as_view(), name="detail"),
    path("<int:pk>/", show_by_heading_view, name="show_by_heading"),
    path("comment/edit/<int:pk>/", EditCommentsView.as_view(), name="edit_comment"),
    path("comment/<str:key>/<int:pk>/", DoubleCommentView.as_view(), name="comment"),
    path("article_delete/<int:pk>/", ArticleDeleteView.as_view(), name="article_delete"),
    path("article_edit/<int:pk>/", ArticleEditView.as_view(), name="article_edit"),
    path("add_article/<int:pk>/", AddArticleView.as_view(), name="add_article"),
    path("add_heading/<int:pk>/", headingcreateview, name="add_heading"),
    path("resurrection/", ArticleResurrectionView.as_view(), name="resurrection"),
    path("", ArticlesMainView.as_view(), name="articles_main"),

]
