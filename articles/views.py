from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import *
from .forms import *
import unidecode
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.db.transaction import atomic
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from boats.decorators import login_required_message, MessageLoginRequiredMixin


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
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword) | Q(
            title__icontains=keyword_unidecode) | Q(content__icontains=keyword_unidecode)
        list_of_articles = list_of_articles.filter(q)
    else:
        keyword = ""
    form = SearchForm(initial={"keyword": keyword})
    paginator = Paginator(list_of_articles, 10)
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
        if self.request.user.is_authenticated:
            context['user'] = ExtraUser.objects.get(pk=self.request.user.pk)
        context["comments"] = Comment.objects.filter(foreignkey_to_article_id=self.kwargs["pk"])
        return context


"""контроллер добавления новой статьи"""


class AddArticleView( SuccessMessageMixin, MessageLoginRequiredMixin, CreateView):
    model = Article
    template_name = "articles/create_article.html"
    form_class = ArticleForm
    success_message = "Article '%(title)s' has been successfully saved"
    redirect_message = "You must be authenticated in order to create new article"

    def get_initial(self):
        self.initial = CreateView.get_initial(self)
        self.initial["author"] = self.request.user
        if self.kwargs["pk"] and self.kwargs["pk"] != 0:
            self.initial["foreignkey_to_subheading"] =\
                get_object_or_404(SubHeading, pk=self.kwargs["pk"])
        try:  # устанавливаем нач. знач поля foreignkey_to_boat если заходим с категории                    #Articles on boats
            current_subheading = get_object_or_404(SubHeading, pk=self.kwargs["pk"])
            self.initial["foreignkey_to_boat"] = current_subheading.one_to_one_to_boat
        except Http404:
            pass
        return self.initial.copy()

    def get_success_url(self):
        """ передача через гет параметры кода того, была ли создана статьия из boats:detail. Нужно
        для корректной работы кнопки Back to Heading Или back to boat в зависимости откуда была
        создана статья"""
        referer = self.request.POST.get("button", None)
        if referer and "boats" in referer:
            code = "boats"
        else:
            code = "articles"
        return "%s?code=%s" % (reverse('articles:detail',
                    args=(self.object.foreignkey_to_subheading.pk, self.object.pk,)), code)


""" контроллер редактирования статьи"""


class ArticleEditView(SuccessMessageMixin, MessageLoginRequiredMixin, UpdateView):
    model = Article
    template_name = "articles/article_edit.html"
    form_class = ArticleForm
    success_message = "Article %(title)s has been edited and saved successfully "
    redirect_message = "You must be authenticated in order to edit this article"

    def get_success_url(self):
        return reverse('articles:detail',
                       args=(self.object.foreignkey_to_subheading.pk, self.object.pk, ))

    def get(self, request, *args, **kwargs):
        if self.get_object().author == self.request.user:
            return UpdateView.get(self, request, *args, **kwargs)
        else:
            messages.add_message(request, messages.WARNING,
                                 "You can only edit your own entries!",
                                 fail_silently=True)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


""" контроллер удаления  статьи"""


class ArticleDeleteView(MessageLoginRequiredMixin, DeleteView):
    model = Article
    template_name = "articles/article_delete.html"
    redirect_message = "You must be authenticated in order to delete this article"

    def get_success_url(self):
        return reverse('articles:show_by_heading',
                       args=(self.object.foreignkey_to_subheading.pk, ))

    def get(self, request, *args, **kwargs):
        if self.get_object().author == self.request.user:
            return DeleteView.get(self, request, *args, **kwargs)
        else:
            message = 'Dear %s, you can only delete your own articles. This article has been' \
                      ' created by %s' % (self.request.user, self.get_object().author)
            messages.add_message(request, messages.WARNING, message=message, fail_silently=True, )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def post(self, request, *args, **kwargs):
        message = "Article %(name)s has deleted from the database" % {"name": self.get_object(
        ).title}
        messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True,
                             extra_tags="alert alert-info")
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
            self.initial["foreignkey_to_article"] = get_object_or_404(Article,
                                                                      pk=self.kwargs["pk"])
        else:
            self.initial["foreignkey_to_boat"] = get_object_or_404(BoatModel,
                                                                   pk=self.kwargs["pk"])
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


""" Контроллер добавления ап-категории и субкатегории"""


@atomic
@login_required_message(message="You must be logged in in order to create new heading")
@login_required
def headingcreateview(request, pk):
    form1 = UpperHeadingForm(request.POST or None, prefix="form1", pk=pk)
    form2 = SubHeadingForm(request.POST or None, prefix="form2", pk=pk)
    context = {"form1": form1, "form2": form2}
    if request.method == "POST":
        if form1.is_valid() and form2.is_valid():
            upperheading = form1.save()
            subheading = form2.save(commit=False)
            subheading.foreignkey = upperheading
            subheading.save()
            message = "You have successfully added an upper-heading\xa0\"" + \
                      upperheading.name + "\""
            messages.add_message(request, messages.SUCCESS, message=message,
                                 fail_silently=True)
            return HttpResponseRedirect(reverse_lazy("articles:articles_main"))
        elif form2.is_valid() and pk != 0:
            subheading = form2.save(commit=False)
            subheading.foreignkey = get_object_or_404(UpperHeading, pk=pk)
            subheading.save()
            message = 'You have successfully added a sub-heading  "%s"' % subheading.name
            messages.add_message(request, messages.SUCCESS, message=message,
                                 fail_silently=True)
            return HttpResponseRedirect(reverse_lazy("articles:articles_main"))
        else:
            messages.add_message(request, messages.WARNING,
                                 "Forms are not valid. Please check the data",
                                 fail_silently=True)
            return render(request, "articles/add_heading.html", context)
    else:
        return render(request, "articles/add_heading.html", context)


""" Контроллер восстановления статей"""


class ArticleResurrectionView(MessageLoginRequiredMixin, FormView):
    model = Article
    form_class = ArticleResurrectionForm
    template_name = "articles/resurrection.html"
    success_url = reverse_lazy("articles:articles_main")
    redirect_message = "You have to be logged in to recover articles "

    def get_form_kwargs(self):
        kwargs = FormView.get_form_kwargs(self)
        kwargs["author_id"] = self.request.user.pk
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            articles = Article.default.filter(id__in=request.POST.getlist('pk')).only("title")
            message = "Articles "
            for counter, article in enumerate(articles):
                if counter == (len(articles)-1):
                    message += " " + article.title + " "
                else:
                    message += " " + article.title + ", "
            message += ' are restored, totally - %s articles' % len(articles)
            messages.add_message(request, messages.SUCCESS, message=message,
                                 fail_silently=True)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
