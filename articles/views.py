from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import *
from .forms import *
import unidecode
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

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


class ContentListView(DetailView):
    template_name = "articles/content.html"
    model = Article


class AddArticleView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Article
    template_name = "articles/create_article.html"
    form_class = ArticleForm
    success_message = "Article %(title)s has been successfully saved"

    def get_initial(self):
        self.initial = CreateView.get_initial(self)
        self.initial["author"] = self.request.user
        if self.kwargs["pk"] and self.kwargs["pk"] != 0:
            self.initial["foreignkey_to_subheading"] =\
                get_object_or_404(SubHeading, pk=self.kwargs["pk"])
        return self.initial.copy()

    def get_success_url(self):
        return reverse('articles:detail',
                       args=(self.object.foreignkey_to_subheading.pk, self.object.pk, ))
