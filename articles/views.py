from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import *
from .forms import *
import unidecode
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

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

    def get_context_data(self, **kwargs):
        context = DetailView.get_context_data(self, **kwargs)
        if self.request.user.is_active and self.request.user.is_activated:
            context['user'] = ExtraUser.objects.get(pk=self.request.user.pk)
        return context


"""контроллер добавления новой статьи"""


class AddArticleView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Article
    template_name = "articles/create_article.html"
    form_class = ArticleForm
    success_message = "Article '%(title)s' has been successfully saved"

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


""" контроллер редактирования статьи"""


class ArticleEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Article
    template_name = "articles/article_edit.html"
    form_class = ArticleForm
    success_message = "Article %(title)s has been edited and saved successfully "

    def get_success_url(self):
        return reverse('articles:detail',
                       args=(self.object.foreignkey_to_subheading.pk, self.object.pk, ))

    def get(self, request, *args, **kwargs):
        if self.get_object().author == self.request.user:
            return UpdateView.get(self, request, *args, **kwargs)
        else:
            messages.add_message(request, messages.WARNING, "You can only edit your own entries!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


""" контроллер удаления  статьи"""


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = "articles/article_delete.html"

    def get_success_url(self):
        return reverse('articles:show_by_heading', args=(self.object.foreignkey_to_subheading.pk, ))

    def get(self, request, *args, **kwargs):
        if self.get_object().author == self.request.user:
            return DeleteView.get(self, request, *args, **kwargs)
        else:
            messages.add_message(request, messages.WARNING,
                                 "You can only delete your own entries!", fail_silently=True, )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS,
                             "Article has deleted from the database",
                             fail_silently=True, extra_tags="alert alert-info")
        return DeleteView.post(self, request, *args, **kwargs)


"""контроллер комментов"""


class DoubleCommentView(SuccessMessageMixin, CreateView):
    model = Comment
    template_name = 'comment/comment_form.html'
    success_message = "Dear %(author)s, thank you for your valuable comment"
    form_class = ArticleCommentForm

    """
    def get_form(self, form_class=None):
        if self.kwargs["key"] == "article":
            form_class = ArticleCommentForm
        else:
            form_class = BoatCommentForm
        return form_class(**self.get_form_kwargs()) 
        """

    def get_initial(self):
        self.initial = CreateView.get_initial(self)
        if self.request.user.is_authenticated:
            self.initial["author"] = self.request.user.username
        if self.kwargs["key"] == "article":
            self.initial["foreignkey_to_article"] = get_object_or_404(Article, pk=self.kwargs["pk"])
        else:
            self.initial["foreignkey_to_boat"] = get_object_or_404(BoatModel, pk=self.kwargs["pk"])
        return self.initial.copy()

    def get_success_url(self):
        if self.kwargs["key"] == "article":
            return reverse('articles:detail', args=(get_object_or_404(Article, pk=self.kwargs[
                "pk"]).foreignkey_to_subheading.pk, self.object.foreignkey_to_article.pk))
        else:
            return reverse("boats:boat_detail",
                           args=(BoatModel.objects.get(pk=self.kwargs["pk"]).pk, ))

    def get_form_kwargs(self):
        kwargs = CreateView.get_form_kwargs(self)
        kwargs["key"] = self.kwargs.get('key')
        return kwargs

