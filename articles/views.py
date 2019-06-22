from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.core.paginator import Paginator
from django.db.models import Q
from fancy_cache import cache_page
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView, FormView
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import *
from .forms import *
import unidecode
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.db.transaction import atomic
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from boats.decorators import login_required_message, MessageLoginRequiredMixin
from django.utils.decorators import method_decorator
from django.core.cache import cache


def vary_on_user_is_authenticated(request):
    """Функция для key_prefix"""
    return request.user.is_authenticated

"""контроллер гл. стр. артиклес"""


#  инвалидация в сигналах по урлу
@method_decorator(cache_page(60*60*24*7, key_prefix=vary_on_user_is_authenticated), name='dispatch')
class ArticlesMainView(TemplateView):
    template_name = "articles/articles_index.html"


""" контроллер показывающий статьи по под-рубрикам + поиск + пагинатор """


def vary_on_paginated_or_not(request):
    pk = request.get_full_path_info().split("/")[-2]
    # Смотрим есть ли на странице пагинация или нет по кол-ву выводимых объектов
    count_eq = Article.objects.filter(foreignkey_to_subheading=int(pk)).count()
    # время удаления последней статьи
    try:
        change_date_of_deleted_article = Article.default.filter(foreignkey_to_subheading=int(
            pk), show=False).values_list("change_date", flat=True).latest("change_date")
        timedelta = (datetime.datetime.now() - change_date_of_deleted_article).seconds > 1
    except (ObjectDoesNotExist, TypeError):
        timedelta = True
    return "show_by_heading_view+%s+%s+%s" % (True if count_eq > 10 else False,
                                           request.user.is_authenticated, timedelta)


#  инвалидация в сигналах по урлу и по key_prefix
@cache_page(60*60*24*7, key_prefix=vary_on_paginated_or_not)
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


def contentlistview_key_prefix(request):
    pk = int(request.get_full_path_info().split("/")[-2])
    #  время последнего изменения статьи
    last_change = Article.objects.filter(pk=pk).values("change_date")[0].get("change_date")
    #  разница текущего времени и времени последнего изменения статьи. Нужна для того, чтобы
    #  различать ситуации когда нужно или не нужно выводить сообщения. Т.е имеем 2 версии кеша
    #  1) с сообщением 2) без сообщения
    timedelta = (datetime.datetime.now() - last_change).seconds > 1 if last_change else True
    try:
        last_change_comments = Comment.objects.filter(foreignkey_to_article_id=pk).values_list(
                                                "change_date", flat=True).latest("change_date")
        timedelta2 = (datetime.datetime.now() - last_change_comments).seconds > 1
    except ObjectDoesNotExist:
        timedelta2 = True
    return "ContentListView+%s+%s+%s" % (vary_on_user_is_authenticated(request), timedelta,
                                         timedelta2)


#  инвалидация по урлу в сигналах
@method_decorator(cache_page(60*60*24*7, key_prefix=contentlistview_key_prefix), name="dispatch")
class ContentListView(DetailView):
    template_name = "articles/content.html"
    model = Article

    def get_context_data(self, **kwargs):
        context = DetailView.get_context_data(self, **kwargs)
        if self.request.user.is_authenticated:
            context['user'] = ExtraUser.objects.get(pk=self.request.user.pk)
        context["comments"] = Comment.objects.filter(foreignkey_to_article_id=self.kwargs["pk"])
        context["allowed_comments"] = \
           (self.request.get_signed_cookie('allowed_comments', default=None))
        return context


"""контроллер добавления новой статьи"""


#  без кеширования
class AddArticleView(SuccessMessageMixin, MessageLoginRequiredMixin, CreateView):
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
        """ передача через гет параметры кода того, была ли создана статьия из boats:detail.
         Нужно для корректной работы кнопки Back to Heading Или back to boat в зависимости
         откуда была создана статья"""
        referer = self.request.POST.get("button", None)
        if referer and "boats" in referer:
            code = "boats"
        else:
            code = "articles"
        return "%s?code=%s" % (reverse('articles:detail',
                    args=(self.object.foreignkey_to_subheading.pk, self.object.pk,)), code)


""" контроллер редактирования статьи"""


#  без кеширования
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


#  кеширование в шаблоне
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
            messages.add_message(request, messages.WARNING, message=message, fail_silently=True,)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def post(self, request, *args, **kwargs):
        message = "Article %(name)s has deleted from the database" % {"name": self.get_object(
        ).title}
        messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True,
                             extra_tags="alert alert-info")
        return DeleteView.post(self, request, *args, **kwargs)


"""Контроллер редактирования комментов"""


#  без  кеша
class EditCommentsView(UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Comment
    template_name = 'comment/comment_form.html'
    success_message = "Dear %(author)s, you have successfully edited your comment "
    form_class = ArticleCommentForm
    permission_denied_message = "You can edit only comments left by yourself"
    raise_exception = False

    def get_success_url(self):
        if self.object.foreignkey_to_article:
            return reverse('articles:detail', args=(Article.objects.get(
                pk=self.object.foreignkey_to_article_id).foreignkey_to_subheading_id,
                                                    self.object.foreignkey_to_article_id))
        else:
            return reverse("boats:boat_detail",
                args=(BoatModel.objects.get(pk=self.object.foreignkey_to_boat_id).pk, ))

    def get_form_kwargs(self):
        """Передаем маркер в формы, чтобы у зарегестрированного пользователя отключить
         возможность редактирования поля имени. """
        kwargs = UpdateView.get_form_kwargs(self)
        if self.request.user.is_authenticated:
            kwargs["author"] = "authenticated"
        return kwargs

    def test_func(self):
        return self.request.user.username == self.get_object().author and \
                self.request.user.is_authenticated or str(self.get_object().pk) in \
                self.request.get_signed_cookie('allowed_comments', default=None) and not \
                self.request.user.is_authenticated


"""контроллер добавления комментов"""


# без кеша
class DoubleCommentView(SuccessMessageMixin, CreateView):
    model = Comment
    template_name = 'comment/comment_form.html'
    success_message = "Dear %(author)s, thank you for your valuable comment"
    form_class = ArticleCommentForm

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
        """Передаем маркер в формы, чтобы у зарегестрированного пользователя отключить
        возможность редактирования поля имени. """
        kwargs = CreateView.get_form_kwargs(self)
        if self.request.user.is_authenticated:
            kwargs["author"] = "authenticated"
        return kwargs

    def get_context_data(self, **kwargs):
        """Передаем либо объект лодки либо статьи"""
        context_data = CreateView.get_context_data(self, **kwargs)
        context_data["instance"] = self.initial.get("foreignkey_to_article",
                                                    self.initial.get("foreignkey_to_boat"))
        return context_data

    def form_valid(self, form):
        """Устанавливаем  куки для незарегестрированных пользователей. заносим значения пк
        созданного объекта комментов в куки для того, чтобы данные пользователи обладающие
        данными
        куками в последствии могли редактировать  свои комменты.
        пример кук:
        '42, 43, 1, 9, 50, 51:1hVs8G:lL7LoWgvybCofo06FTwJcJa6G1w'"""
        response = super().form_valid(form)
        existing_allowed_comments = self.request.get_signed_cookie('allowed_comments',
                                                                   default=None)
        if not self.request.user.is_authenticated:
            if existing_allowed_comments and str(self.object.pk) not in \
                    existing_allowed_comments:
                response.set_signed_cookie('allowed_comments',
                                        ", ".join([existing_allowed_comments,
                                                   str(self.object.pk)]))
            elif not existing_allowed_comments:
                response.set_signed_cookie('allowed_comments', str(self.object.pk))
        return response


""" Контроллер добавления ап-категории и субкатегории"""


# без кеша
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


#  инвалидация кеша в сигналах и в формах стр. 183
@method_decorator(cache_page(60*60*24*7, key_prefix=vary_on_user_is_authenticated), name="dispatch")
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
            message += ' are restored, totally - %s articles' % len(articles) if len(articles) \
                             > 1 else ' are restored, totally - %s article' % len(articles)
            messages.add_message(request, messages.SUCCESS, message=message,
                                 fail_silently=True)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
