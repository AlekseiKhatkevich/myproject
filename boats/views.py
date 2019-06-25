from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages, auth
from django.core.signing import BadSignature
from articles.models import Article, Comment, ArticleManager
from .forms import *
import boats.utilities
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.db.transaction import atomic
from django.db.models import Prefetch,  Min, Q
from django.core.mail import send_mail, BadHeaderError
from ratelimit.mixins import RatelimitMixin
from extra_views import SearchableListMixin
from .decorators import login_required_message, MessageLoginRequiredMixin
from .render import Render, link_callback
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.utils.decorators import method_decorator
from reversion.models import Version
from reversion.views import RevisionMixin, create_revision
from reversion import RevertError
import os
from django.core.cache import cache
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from fancy_cache import cache_page
from django.core.cache.utils import make_template_fragment_key
from django.conf import settings
from django.views.decorators.gzip import gzip_page
from django.core.exceptions import FieldDoesNotExist
from django.contrib.contenttypes.models import ContentType


"""Контроллер редактирования данных о лодке"""


@atomic
@login_required_message(message=_("You must be logged in in order to edit this boat entry"))
@login_required
def viewname_edit(request, pk):
    obj1 = BoatModel.objects.get(pk=pk)
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1",
                         instance=obj1, pk=pk)
        form2 = boat_image_inline_formset(request.POST, request.FILES, prefix="form2",
                                          instance=obj1)
        if form1.is_valid() and form2.is_valid():
            if form1.has_changed() or form2.has_changed():
                boat_obj = form1.save()
                form2.save()
                message = "You successfully edited %(name)s  data" % {"name":
                                                                          boat_obj.boat_name}
                messages.add_message(request, messages.SUCCESS, message=message,
                                     fail_silently=True)
                return HttpResponseRedirect(reverse_lazy("boats:boat_detail", args=(pk, )))
            else:
                messages.add_message(request, messages.INFO,
                                     "You have changed nothing in this form yet",
                                     fail_silently=True)
                context = {"form1": form1, "form2": form2}
                return render(request, "edit_boat.html", context)
        else:
            messages.add_message(request, messages.WARNING,
                                 "Forms are not valid. Please check the data",
                                 fail_silently=True)
            context = {"form1": form1, "form2": form2}
            return render(request, "edit_boat.html", context)
    else:
        if request.user == obj1.author:
            form1 = BoatForm(prefix="form1", instance=obj1, pk=pk)
            form2 = boat_image_inline_formset(prefix="form2", instance=obj1)

            context = {"form1": form1, "form2": form2}
            return render(request, "edit_boat.html", context)
        else:
            messages.add_message(request, messages.WARNING, "You can only edit your own "
            "entries!", extra_tags="text-muted  font-weight-bold", fail_silently=True)
            return redirect(request.META.get('HTTP_REFERER'))


""" Контроллер удаления лодки"""


#  кеширование в шаблоне  None
@method_decorator([login_required_message(message="You must be logged in in order to delete this boat entry"), login_required], name="dispatch")
class BoatDeleteView(DeleteView):
    model = BoatModel
    success_url = reverse_lazy("boats:boats")
    template_name = "delete_boat.html"

    def post(self, request, *args, **kwargs):
        message = 'Boat "%s"  has deleted from the database' % self.get_object().boat_name
        messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True,
                             extra_tags="alert alert-info")
        #  удаляем кеш шаблона "boat_detail_view", куска который отвечает за изображения для
        #  того, чтобы после  восстановления лодки  отображались фотографии на ее странице
        pk = self.kwargs.get("pk")
        data_obj = cache.get("boat_detail_view" + str(pk), None)
        if data_obj:
            eq_images = data_obj.get("eq_images")
            key1 = make_template_fragment_key("boat_detail_images", [eq_images, True])
            key2 = make_template_fragment_key("boat_detail_images", [eq_images, False])
            cache.delete_many((key1, key2))
        return DeleteView.post(self, request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return DeleteView.dispatch(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = DeleteView.get_context_data(self, **kwargs)
        if self.user_id:
            context['user'] = ExtraUser.objects.get(pk=self.user_id)
        context["bool"] = self.request.user == self.object.author
        return context


""" Индекс"""


#  кэширование в шаблоне 60*60*24*7
class IndexPageView(TemplateView):
    template_name = "index.html"


""" список всех лодок"""


def vary_on_database(request):
    cache_key = "BoatListView"
    data_obj = cache.get(cache_key)
    if not data_obj:
        change_obj = BoatModel.objects.all().values_list("change_date", flat=True).latest(
                "change_date").timestamp()
        count_obj = BoatModel.objects.all().count()
        data_obj = "%s+%s" % (change_obj, count_obj)
        cache.set(cache_key, data_obj, 60*60*24)
    return "BoatListView+%s+%s" % (str(data_obj), str(request.user.is_authenticated))


@method_decorator(cache_page(60*60*24, key_prefix=vary_on_database), name="dispatch")
class BoatListView(SearchableListMixin, ListView):
    model = BoatModel
    template_name = "boats.html"
    paginate_by = 10
    search_fields = ["boat_name", ]

    def get_ordering(self):
        """метод возвращает поле по которому идет сортировка!"""
        self.field = self.request.GET.get('ordering')
        self.mark = self.request.GET.get("mark")
        if self.field == '' or self.mark == "":
            messages.add_message(self.request, messages.WARNING, message="Please choose "
                                            "sorting pattern", fail_silently=True)
            return None
        if all([self.field, self.mark]):
            try:
                self.verbose_name = BoatModel._meta.get_field(self.field).verbose_name
            except FieldDoesNotExist:  # на случай сортировки по "Comments count" так как это
                # все таки вычисляемое поле
                self.verbose_name = "Comments count"
            message = 'Boats are ordered by:\xa0\"' + self.verbose_name + "\"\xa0in\xa0" + \
                      self.mark + "\xa0order"
            if self.field != self.request.COOKIES.get("ordering") or \
                    self.mark != self.request.COOKIES.get("mark"):
                messages.add_message(self.request, messages.SUCCESS, message=message,
                                     fail_silently=True)
            if self.mark == "descending" and self.field != "order_by_comment_count":
                self.field = "-" + self.field
            return self.field if self.field != "order_by_comment_count" else None

    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        context["images"] = BoatImage.objects.all().distinct('boat')  # выбирает только 1
        # уникальный объект из группы объектов с  одинаковым фк, остальные отсеивает
        if self.field and self.mark:
            context["verbose_name"] = self.verbose_name
        return context

    def render_to_response(self, context, **response_kwargs):
        """Для корректного возврата после поиска к отсортированному списку. Сохраняем
        сортировку в куках, а затем извлекаем ее в шаблоне и запихиваем в УРЛ через ГЕТ
        параметры"""
        response = ListView.render_to_response(self, context, **response_kwargs)
        if all([self.field, self.mark]):
            if self.field.startswith("-"):
                self.field = self.field[1:]
            response.set_cookie('ordering', self.field)
            response.set_cookie("mark", self.mark)
        return response

    def get_queryset(self):
        """фильтрация кс при нажатии на флажок по стране"""
        qs = SearchableListMixin.get_queryset(self)
        country = self.request.GET.get('country', False)
        if country:
            boat = qs.filter(boat_country_of_origin=country).only("boat_country_of_origin")[
                   :1].iterator()
            message = 'Boats are filtered by county "%s"' % next(
                boat).boat_country_of_origin.name
            messages.add_message(self.request, messages.SUCCESS, message=message,
                                 fail_silently=True)
            return qs.filter(boat_country_of_origin=country)
        #  фильтрация по кол-ву комментов
        if self.field == "order_by_comment_count" and all([self.field, self.mark]):
            return qs.order_by_comment_count_desc() if self.mark == "descending" else \
                qs.order_by_comment_count_asc()
        return qs


""" просмотр  детальной информации о лодке"""


#  кэширование в шаблоне , инвалидация ключа data_obj в сигналах и медоте клин
#  ArticleResurrectionForm
def boat_detail_view(request, pk):
    pr = Prefetch("article_set", queryset=Article.objects.all().exclude(show=False).only(
        "change_date", 'title'))
    current_boat = BoatModel.objects.prefetch_related("boatimage_set", "comment_set", pr).get(pk=pk)
    images = current_boat.boatimage_set.all()
    comments = current_boat.comment_set.all()
    articles = current_boat.article_set(manager='reverse').all()
    versions = Version.objects.select_related("revision").\
        get_for_object_reference(BoatModel, pk).only("id", "revision")
    allowed_comments = request.get_signed_cookie('allowed_comments', default=None)

    data_obj = cache.get("boat_detail_view" + str(current_boat.pk))
    if not data_obj:
        eq_images = images.values_list("change_date", flat=True).latest("change_date") \
            if images else None
        eq_current_boat = BoatModel.objects.filter(pk=pk).values_list("change_date",
                                                            flat=True).latest("change_date")
        eq_articles = (articles.values_list("change_date", flat=True).latest("change_date") \
            if articles else None, articles.count())
        eq_versions = versions.values_list("revision__date_created", flat=True).\
            latest("revision__date_created") if versions else None
        eq_comments = comments.values_list("change_date", flat=True).latest("change_date")\
            if comments else None
        EQ = {"eq_images": eq_images, "eq_current_boat": eq_current_boat, "eq_articles":
            eq_articles, "eq_versions": eq_versions, "eq_comments": eq_comments}
        cache.set("boat_detail_view" + str(current_boat.pk), EQ, 60 * 60 * 24)
    else:
        EQ = data_obj

    context = {"images": images, "current_boat": current_boat, "comments": comments,
               "articles": articles, "versions": versions,
               "allowed_comments": allowed_comments, "EQ": EQ}

    if request.method == "GET":
        return render(request, "boat_detail.html", context)
    else:
        version_num = request.POST.get("rollback")
        if version_num == "":
            messages.add_message(request, messages.WARNING, message=
            "Please choose the rollback point date", fail_silently=True)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        elif current_boat.author != request.user:
            messages.add_message(request, messages.WARNING, message="You can only rollback your                                                     own entries", fail_silently=True)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        return HttpResponseRedirect(reverse_lazy("boats:rollback",  args=(pk, version_num)))


""" Контроллер отката версий лодки"""


# кеширование в шаблоне  60*60*24
class RollbackView(MessageLoginRequiredMixin, RevisionMixin, DetailView):
    template_name = "rollback.html"
    model = BoatModel
    redirect_message = "You have to be authenticated to rollback boat's data"
    revision_manage_manually = True  # не сохраняем новую версию при откате (при вызове
    # self.get_object().save() в методе ПОСТ)

    def get_context_data(self, **kwargs):
        context = DetailView.get_context_data(self, **kwargs)
        #  объект выбранной версии
        version = Version.objects.select_related("revision").get(id=self.kwargs["version_id"])
        #  список всех полей модели
        fields = [f.name for f in BoatModel._meta.get_fields(include_parents=False)]
        boat = {}
        #  собираем контекст лодки из версии для отображения состояния лодки на момент сохранения
        #  версии
        for fld in fields:
            try:
                boat[fld] = version.field_dict[fld]
            except KeyError:
                boat[fld] = "DoesNotExists"
        boat.update({"author": version.revision.user})
        context.update({"boat": boat, "version": version})
        # самая старая фотка (пока не используется)
        minimal_id = BoatImage.objects.aggregate(min=Min('id', filter=Q(boat_id=self.kwargs[
            "pk"])))
        try:
            #  получаем одну фотку из текущей (выбранной) версии. Объект сохраненной лодки и
            #  объект сохраненного изображения имеют один и тот же revision_id но разный
            #  content_type_id. Через это можно установить взаимосвязь
            image_version = Version.objects.filter(revision_id=version.revision_id,
            content_type_id=ContentType.objects.get(model="boatimage").id).\
                only("object_id").order_by("?").first()
            image = BoatImage.objects.get(pk=image_version.object_id)
            context["image"] = image
        except (ObjectDoesNotExist, AttributeError):
            pass
        return context

    def post(self, request, *args, **kwargs):
        # получаем необходимую версию записи и откатываемся до нее
        version = Version.objects.get(id=self.kwargs["version_id"])
        try:
            version.revision.revert()
        except RevertError as err:
            messages.add_message(self.request, messages.ERROR, message=str(err),
                                 fail_silently=True)
            return redirect(request.META.get('HTTP_REFERER'))
        #  сайв нужен для привязки /перепривязки категорий статей
        self.get_object().save()
        # если файл  изображения был фактически удален и его путь в бд ведет в никуда то мы его
        # удаляем из БД чтобы пустой путь не был привязан к объекту изображения
        images = self.get_object().boatimage_set.all()
        score = 0
        for image in images:
            try:
                if not os.path.exists(image.boat_photo.path):
                    image.true_delete(self)  # удаляем по настоящему
                    score += 1
            except NotImplementedError:
                pass
        if score != 0:
            message = "%d broken image instances  has been deleted from DB" % score
            messages.add_message(request, messages.WARNING, message=message,
                                 fail_silently=True)
        message = "You successfully rolled back %(name)s  data. Rollback date is %(date)s " \
                  % ({"name": self.get_object().boat_name, "date":
            version.revision.date_created})
        messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True)
        return HttpResponseRedirect(reverse_lazy('boats:boat_detail',
                                                 args=(self.kwargs["pk"], )))

    def dispatch(self, request, *args, **kwargs):
        """только автор лодки может делать роллбэк"""
        if self.request.user != self.get_object().author:
            messages.add_message(request, messages.WARNING, "You can only rollback your own "
                                                            "entries", fail_silently=True)
            return self.handle_no_permission()
        return MessageLoginRequiredMixin.dispatch(self, request, *args, **kwargs)


""" Контроллер добавления новой лодки"""


#  кеширование в шаблоне "60*60*24"
@atomic
@login_required_message(message="You must be logged in in order to create new boat entry")
@login_required
def viewname(request):
    form1 = BoatForm(request.POST or None, request.FILES or None, prefix="form1")
    if request.method == 'POST':
        if "add_row" in request.POST:
            cp = request.POST.copy()
            cp['form2-TOTAL_FORMS'] = int(cp['form2-TOTAL_FORMS']) + 1
            form2 = boat_image_inline_formset(cp, request.FILES, prefix="form2")
            context = {"form1": form1, "form2": form2}
            # для предотвращения появления ошибок про добавлении нового рядя
            form1.errors.clear(), form2.errors.clear()
            return render(request, "create.html", context)
        elif form1.is_valid():
            prim = form1.save(commit=False)
            prim.author = request.user
            form2 = boat_image_inline_formset(request.POST, request.FILES, prefix="form2",
                                              instance=prim)
        else:
            form2 = boat_image_inline_formset(request.POST, request.FILES, prefix="form2")
            context = {"form1": form1, "form2": form2}
            return render(request, "create.html", context)
        if form2.is_valid():
            boat = form1.save()
            form2.save()
            message = "You successfully added a boat called:\xa0" + boat.boat_name
            messages.add_message(request, messages.SUCCESS, message=message,
                                 fail_silently=True)
            return HttpResponseRedirect(reverse_lazy("boats:boat_detail", args=(prim.pk, )))
        else:
            form2 = boat_image_inline_formset(request.POST, request.FILES, prefix="form2",
                                              instance=prim)
            context = {"form1": form1, "form2": form2}
            return render(request, "create.html", context)
    else:
            form2 = boat_image_inline_formset(prefix="form2")
            context = {"form1": form1, "form2": form2}
            return render(request, "create.html", context)


""" контроллер LOGIN"""


@method_decorator([cache_page(60*60*24*7), vary_on_cookie], name="dispatch")
class AdminLoginView(SuccessMessageMixin, LoginView):
    template_name = "admin/login.html"
    success_message = "You have logged in, %(username)s"
    form_class = AuthCustomForm


""" контроллер LOGOUT"""


#  кешированеи в шаблоне None
@method_decorator(cache_page(None), name="dispatch")
class AdminLogoutView(LoginRequiredMixin, LogoutView):
    template_name = "admin/logout.html"

    def get(self, request, *args, **kwargs):
        message = "You have logged out"
        messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True)
        logout(request)
        return LogoutView.get(self, request, *args, **kwargs)


""" контроллер страницы профиля пользователя"""


def vary_on_user_profile(request):
    try:
        eq_boats_by_user = BoatModel.objects.filter(
        author=request.user).order_by("-boat_publish_date")[:10].values_list("change_date",
                                                                             flat=True)[0]
    except IndexError:
        eq_boats_by_user = None
    try:
        eq_articles_by_user = Article.objects.filter(author=request.user).exclude(
        change_date__isnull=True).order_by("-created_at")[: 10].values_list("change_date",
                                                                            flat=True)[0]
    except IndexError:
        eq_articles_by_user = None
    try:
        eq_comments_by_user = Comment.objects.filter(Q(
            foreignkey_to_article__author=request.user,
        is_active=True) | Q(foreignkey_to_boat__author=request.user,
                            is_active=True)).order_by(
        "-created_at")[: 5].values_list("change_date", flat=True)[0]
    except IndexError:
        eq_comments_by_user = None
    finally:
        eq_user_change_data = ExtraUser.objects.filter(id=request.user.pk).values_list(
            "change_date", flat=True).latest("change_date")
    EQ = (eq_boats_by_user, eq_articles_by_user, eq_comments_by_user, eq_user_change_data)
    #  для того, чтобы мессадж о успешном входе показывался только после успешного логина, а не
    #  всегда
    timedelta = (datetime.datetime.now() - request.user.last_login).seconds > 1
    #  для того, чтобы мессадж о смене данных показывался только после смены данных , а не всегда
    temedelta2 = (datetime.datetime.now() - request.user.change_date).seconds > 1
    return "UserProfileView + %s + %s + %s " % (EQ,  timedelta, temedelta2)


@method_decorator(cache_page(60*60*24*7, key_prefix=vary_on_user_profile), name="dispatch")
class UserProfileView(LoginRequiredMixin,  TemplateView):
    template_name = "admin/userprofile.html"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context["boats_by_user"] = \
            BoatModel.objects.order_by("-boat_publish_date").\
        filter(author=self.request.user)[:10].only("boat_name", "id")
        context["articles_by_user"] = Article.objects.order_by("-created_at").filter(
            author=self.request.user)[: 10].only("title", "id")
        filter1 = Comment.objects.filter(foreignkey_to_article__author=self.request.user,
                    is_active=True).select_related('foreignkey_to_article', "foreignkey_to_boat")
        filter2 = Comment.objects.filter(foreignkey_to_boat__author=self.request.user,
                    is_active=True).select_related('foreignkey_to_article', "foreignkey_to_boat")
        context["comments_by_user"] = filter1.union(filter2).order_by("-created_at")[: 5]
        return context


""" корректировка данных пользователя"""


#  кеширование в шаблоне "60*60*24*30"
class CorrectUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = ExtraUser
    template_name = "admin/correct_user_info.html"
    form_class = CorrectUserInfoForm
    success_url = reverse_lazy("boats:user_profile")
    success_message = "Your personal data has been corrected, %(username)s"

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return UpdateView.dispatch(self, request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


""" Изменение пароля"""


#  кеширование в шаблоне None
class PasswordCorrectionView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = "admin/password_change.html"
    success_url = reverse_lazy("boats:user_profile")
    success_message = "Your password has been changed. Please confirm the change " \
                      "via email you will have received shortly "
    form_class = PwdChgForm


""" добавление нового пользователя"""


#  кеширование отсутствует
class AddNewUserView(CreateView):
    model = ExtraUser
    template_name = "admin/add_new_user.html"
    form_class = NewUserForm
    success_url = reverse_lazy("boats:register_is_done")


"""контроллер успешной регистрации"""


# кеширование в шаблоне None
class RegisterDoneView(TemplateView):
    template_name = "admin/register_done.html"


""" контроллер активации пользователя через емейл"""


#  кеширование в шаблонах ( 3 штуки)
def user_activate_view(request, sign):  # 575
    try:
        username = boats.utilities.signer.unsign(sign)
    except BadSignature:
        return render(request, "admin/bad_signature.html")
    user = get_object_or_404(ExtraUser, username=username)
    if user.is_activated:
        template = "admin/user_is_activated.html"
    else:
        template = "admin/successful_activation.html"
        user.is_active = True
        user.is_activated = True
        user.save(update_fields=["is_active", "is_activated"])
    return render(request, template)


"""Контроллер удаления зарегестрированного пользователя"""


#  кеширование в шаблоне None
class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = ExtraUser
    template_name = 'admin/delete_user.html'
    success_url = reverse_lazy("boats:index")

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return DeleteView.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "deactivate" in self.request.POST:  # деактивация аккаунта вместо удаления
            user = self.request.user
            user.is_active = user.is_activated = False
            user.save()
            message = 'Your profile "%s" is successfully deactivated.' % \
                      self.request.user.username
            messages.success(request, message=message, fail_silently=True)
            logout(self.request)
            return HttpResponseRedirect(reverse_lazy("boats:index"))
        else:
            logout(request)
            message = 'Your profile  is deleted.'
            messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True)
            return DeleteView.post(self, request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


"""Контроллер формы обратной связи"""


#  без кеша
def feedback_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST, mark=request.user.is_authenticated)
        if form.is_valid():
            name = form.cleaned_data["name"]
            subject = form.cleaned_data["subject"] + " from " + name
            sender = form.cleaned_data["sender"]
            message = form.cleaned_data['message']
            copy = form.cleaned_data['copy']
            recipients = ["hardcase@inbox.ru", ]
            if copy:
                recipients.append(sender)
            try:
                from myproject.settings import EMAIL_HOST_USER
                send_mail(subject, message, EMAIL_HOST_USER, recipients, fail_silently=False)
            except BadHeaderError:
                return HttpResponse("Invalid header found")
            else:
                messages.add_message(request, messages.SUCCESS,
                                     "You have successfully sent your  message to the                                                       administration", fail_silently=True)
                return HttpResponseRedirect(reverse_lazy("boats:index"))
        else:
            context = {"form": form, }
            return render(request, "feedback.html", context)

    else:
        if request.user.is_authenticated:
            #  mark передается в инит формы
            form = ContactForm(initial={"sender": auth.get_user(request).email,
            "name": auth.get_user(request).username}, mark=request.user.is_authenticated)
        else:
            form = ContactForm()
        context = {"form": form, "username": auth.get_user(request).username}
        return render(request, "feedback.html", context)


""" контроллер отправки письма для сброса пароля"""


@method_decorator(cache_page(60*60*24*30), name="dispatch")
class PassResView(RatelimitMixin, SuccessMessageMixin, PasswordResetView):
    success_url = reverse_lazy("boats:index")
    from_email = "hardcase@inbox.ru"
    subject_template_name = 'email/reset_subject.txt'
    email_template_name = "email/reset_email.html"
    success_message = "Dear %(username)s , " \
                      "email with the instructions has been sent to your email - %(email)s"
    template_name = "admin/password_reset.html"
    form_class = PRForm
    ratelimit_key = 'ip'
    ratelimit_rate = '10/5m'
    ratelimit_block = True
    ratelimit_method = ('GET', 'POST')


""" контроллер проверки UID , ключа и сброс пароля"""


@method_decorator(cache_page(60*60*24*30), name="dispatch")
class PassResConfView(SuccessMessageMixin, PasswordResetConfirmView):
    post_reset_login = True
    post_reset_login_backend = "django.contrib.auth.backends.ModelBackend"
    success_url = reverse_lazy("boats:user_profile")
    success_message = "Dear %(username)s , your password has changed . " \
                      "Please do not forget your new password!"
    template_name = "admin/password_reset_confirmation.html"
    form_class = SPForm


"""контроллер рендеринга в PDF  в поток"""


def invalidate_pdf(request):
    pk = request.get_full_path_info().split("/")[-2]
    EQ = cache.get("Pdf+%s" % pk)
    if not EQ:
        current_boat = BoatModel.objects.prefetch_related("boatimage_set").filter(pk=int(pk))
        eq_current_boat = current_boat.values_list("change_date", flat=True).latest(
        "change_date").timestamp()
        eq_images = current_boat[0].boatimage_set.values_list("change_date", flat=True).latest(
        "change_date").timestamp() if current_boat[0].boatimage_set.exists() else None
        images_count = current_boat[0].boatimage_set.count()
        EQ = (eq_current_boat, eq_images, images_count)
        cache.set("Pdf+%s" % pk, EQ, 60*60*24)
    return EQ


@method_decorator(cache_page(60*60*24, key_prefix=invalidate_pdf), name="dispatch")
class Pdf(TemplateView):

    def get(self, request, *args, **kwargs):
        pr = Prefetch("boatimage_set", to_attr="images")
        current_boat = BoatModel.objects.prefetch_related(pr).get(pk=self.kwargs["pk"])
        params = {"current_boat": current_boat, "request": request}
        return Render.render("pdf/pdf.html", params, filename=current_boat.boat_name)


"""контроллер рендеринга в PDF  в файл"""


#  инвалидация через урл в сигналах
@cache_page(60*60*24)
def render_pdf_view(request, pk):
    template_path = "pdf/pdf.html"
    pr = Prefetch("boatimage_set", to_attr="images")
    current_boat = BoatModel.objects.prefetch_related(pr).get(pk=pk)
    context = {"current_boat": current_boat, "request": request}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % (current_boat.boat_name
                                                                     + ".pdf")

    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisaStatus = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funny view
    if pisaStatus.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


""" Список лодок для восстановкления"""


#  кеширование в шаблоне
class ReversionView(MessageLoginRequiredMixin, TemplateView):
    template_name = "reversion.html"
    redirect_message = "You need to be authenticated to recover boat's data"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        # pk всех существующих  в базе лодок
        existing_boats_pk = BoatModel.objects.all().values_list("pk", flat=True).iterator()
        #  Выбираем все удаленные лодки текущим пользователем
        if self.request.user.is_superuser:
            #  показываем лодки без автора для суперюзера
            q = Q(revision__user_id=self.request.user.id) | Q(revision__user_id__isnull=True)
        else:
            q = Q(revision__user_id=self.request.user.id)
        versions = Version.objects.get_for_model(BoatModel).filter(
            q).exclude(object_id__in=existing_boats_pk).order_by("object_id").distinct(
            "object_id")
        context["versions"] = versions
        context["id_eq"] = [version.id for version in versions]
        #  ограничиваев кол-во выдаваемых фоток 3-мя штуками
        memory_limiter = set(BoatImage.objects.filter(boat_id__isnull=True).exclude(
            memory__in=existing_boats_pk).values_list("memory", "pk"))
        cnt = []
        superfluous_images = set()
        for memory in memory_limiter:
            cnt.append(memory[0])
            if cnt.count(memory[0]) > 3:
                superfluous_images.add(memory)
        # фото всех удаленных лодок
        images = BoatImage.objects.filter(boat_id__isnull=True, pk__in=[pk for memory, pk in
                    (memory_limiter - superfluous_images)]).exclude(memory__in=existing_boats_pk)
        # список рк всех фоток не привязанных к лодкам
        images.memory_list = str(images.values_list("memory", flat=True))
        for image in images:
            image.memory = str(image.memory)
        context["images"] = images
        #  передаем имена лодок в следующий контроллер ReversionDeleteView
        version_objects = {version.object_id: version.field_dict.get("boat_name")
                           for version in versions}
        self.request.session["versions"] = version_objects
        return context


"""Контроллер удаления версии"""


#  кеширование в шаблоне
class ReversionDeleteView(MessageLoginRequiredMixin, TemplateView):
    template_name = "reversion_delete.html"
    redirect_message = "You have to be logged in to delete reversions"

    @atomic
    def post(self, request, *args, **kwargs):
        versions = Version.objects.select_related("revision").\
            filter(object_id=self.kwargs.get("pk"))
        images = BoatImage.objects.filter(memory=self.kwargs.get("pk"))
        for version in versions:
            #  удаляем кеш версий роллбэка
            cache_key = make_template_fragment_key('rollback', [version.id, ])
            cache.delete(cache_key)
            version.revision.delete()
            version.delete()
        for image in images:
            try:
                Version.objects.get(object_id=image.pk,
                                    content_type_id=ContentType.objects.get(
                    model="boatimage").id).delete()  # удалаяем версии связанных изображений
            except ObjectDoesNotExist:
                pass
            image.true_delete()
        try:
            del self.request.session["versions"]
        except KeyError:
            self.request.session.get("versions").clean()
        return redirect("boats:reversion")

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context["boat_name"] = self.request.session.get("versions").\
            get(str(self.kwargs.get("pk")))
        context["images"] = BoatImage.objects.filter(memory=self.kwargs.get("pk"))
        context["eq_images"] = context["images"].count() if context["images"] else None
        return context

    def dispatch(self, request, *args, **kwargs):
        """только автор лодки может удалиь данные полностью"""
        if self.request.user.pk != Version.objects.filter(object_id=self.kwargs.get("pk")).only(
                "revision")[:1][0].revision.user_id:
            messages.add_message(request, messages.WARNING, "You can only delete your own "
                                                            "entries", fail_silently=True)
            return self.handle_no_permission()
        return MessageLoginRequiredMixin.dispatch(self, request, *args, **kwargs)


""" Контроллер восстановления конкретной лодки"""


#  кеширование в шаблоне
@create_revision(manage_manually=True)  # не создаем версию при восстановлении лодки
@login_required_message(message="You need to be authenticated to recover boat's data")
@login_required
@atomic
def reversion_confirm_view(request, pk):
    #  Список имен существующих лодок
    existing_boats_names = BoatModel.objects.all().values_list("boat_name",  flat=True)
    #  Текущая версия для восстановления
    versions = Version.objects.get_for_model(BoatModel).filter(object_id=pk)[0:1]
    #  Имя текущей лодки
    current_boat_name = versions[0].field_dict["boat_name"]
    #  РК существующей лодки с таким - же именем, если есть
    try:
        existing_boat_pk = BoatModel.objects.filter(boat_name__iexact=current_boat_name).only(
            "pk")[0].pk
        #  Урл на существующую лодку с таким-же именем
        url = "<a href='" + str((reverse_lazy("boats:boat_detail", args=(existing_boat_pk,
                                                                         ))))\
              + "'>%s</a>" % current_boat_name
        message = 'Boat with the name "%s" is already exist on the site .' \
                  ' You can not restore it! ' % url
    except (IndexError, EmptyResultSet):
        message = "something went wrong"
    #  Если лодка с таким именем уже существует то не даем ее восстановить
    if request.method == "POST":
        if current_boat_name.lower() in map(lambda name: name.lower(), existing_boats_names):
            messages.add_message(request, messages.WARNING, message=mark_safe(message),
                                 fail_silently=True)
            return redirect("boats:reversion")
        else:
            versions[0].revision.revert()
            restored_boat = BoatModel.objects.get(boat_name=versions[0].object_repr)
            restored_boat.save()
            # восстанавливаем комменты тоже
            comments = Version.objects.get_for_model(Comment).filter(
                content_type_id=ContentType.objects.get(model="comment").pk).only(
                "serialized_data").iterator()
            for comment in comments:
                if comment.field_dict.get("foreignkey_to_boat_id") == pk:
                    comment.revision.revert()
            message = 'Boat "%(boat_name)s" is restored!' % {"boat_name":
                                                                 versions[0].object_repr}
            messages.add_message(request, messages.SUCCESS, message=message,
                                 fail_silently=True)
            return HttpResponseRedirect(reverse_lazy("boats:boat_detail",  args=(pk, )))
    else:
        context = {"versions": versions, "current_boat_name": current_boat_name}
        return render(request, "reversion_confirmation.html", context)


"""Контроллер показа объявлений о лодке на https://www.blocket.se """


@method_decorator(cache_page(60*60), name="dispatch")
class BlocketView(DetailView):
    model = BoatModel
    template_name = 'blocket.html'

    def get_context_data(self, **kwargs):
        context = DetailView.get_context_data(self, **kwargs)
        context["blocket"], context['pricelist'], context["cities"] \
            = (boats.utilities.spider(self.kwargs.get("name")))
        rate = boats.utilities.currency_converter(1000)
        context["pricelist_euro"] = []
        for price in context['pricelist']:
                try:
                    context["pricelist_euro"].append(int(price/rate))
                except TypeError:
                    context["pricelist_euro"].append(None)
        cache.set(self.object.id, context["cities"], 60*60*12)
        return context


""" Контроллер просмотра кары с местами продажи лодок """


# кеширование в функции utilities.map_folium
@gzip_page
def map_show(request, pk):
    # запускаем ф-цию map_folium через custom_lru_cache
    boats.utilities.custom_lru_cache(places=cache.get(pk), pk=pk)
    local_path = os.path.join(settings.BASE_DIR, "templates", "maps",  str(pk) + ".html")
    if boats.utilities.define_location():  # на локальной машине
        return FileResponse(open(local_path, "rb"), content_type="text/html")
    else:  # на Heroku
        if os.path.exists(local_path):  # если есть файл на Хероку (дино еще работает)
            return FileResponse(open(local_path, "rb"), content_type="text/html")
        else:  # если файла на хероку нет  то показываем url на карту на aws
            return HttpResponseRedirect(MapTemplateModel.objects.get(
               boat_id=pk).map_template.url)



