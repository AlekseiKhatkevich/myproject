from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import *
from .forms import *
import unidecode

"""контроллер гл. стр. артиклес"""


class ArticlesMainView(TemplateView):
    template_name = "articles/articles_index.html"


""" контроллер показывающий статьи по под-рубрикам + поиск + пагинатор """


def show_by_heading_view(request, pk): #597
    current_heading = get_object_or_404(SubHeading, pk=pk)
    list_of_articles = Article.objects.filter(foreignkey_to_subheading=pk)
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        keyword_unidecode = unidecode.unidecode(keyword)
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword) | Q(title__icontains=keyword_unidecode) | Q(content__icontains=keyword_unidecode)
        list_of_articles = list_of_articles.filter(q)
    else:
        keyword = ""
    form = SearchForm(initial={"keyword": keyword})
    paginator = Paginator(list_of_articles, 7)
    if "page" in request.GET:
        page_num = request.GET["page"]
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {"current_heading": current_heading, "page": page,
               "list_of_articles": page.object_list, "form": form}  # 597
    return render(request, "articles/show_by_subheading.html", context)


""" контроллер просмотра конкретной статьи"""


class ContentListView(ListView):
    template_name = "articles/content.html"
    model = Article

