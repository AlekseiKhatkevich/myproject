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
from .models import *
from articles.models import Article, Comment
from .forms import *
from .utilities import *
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
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
from reversion.models import Version
import os


"""Контроллер редактирования данных о лодке"""


@atomic
@login_required_message(message=_("You must be logged in in order to edit this boat entry"))
@login_required
def viewname_edit(request, pk):
    obj1 = BoatModel.objects.get(pk=pk)
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1", instance=obj1)
        form2 = boat_image_inline_formset(request.POST, request.FILES, prefix="form2", instance=obj1)
        if form1.is_valid() and form2.is_valid():
            if form1.has_changed() or form2.has_changed():
                boat_obj = form1.save()
                form2.save()
                message = "You successfully edited %(name)s  data" % {"name": boat_obj.boat_name}
                messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True)
                return HttpResponseRedirect(reverse_lazy("boats:boat_detail", args=(pk, )))
            else:
                messages.add_message(request, messages.INFO,
                                     "You have changed nothing in this form yet", fail_silently=True)
                context = {"form1": form1, "form2": form2}
                return render(request, "edit_boat.html", context)
        else:
            messages.add_message(request, messages.WARNING,
                                 "Forms are not valid. Please check the data", fail_silently=True)
            context = {"form1": form1, "form2": form2}
            return render(request, "edit_boat.html", context)
    else:
        if request.user == obj1.author:
            form1 = BoatForm(prefix="form1", instance=obj1)
            form2 = boat_image_inline_formset(prefix="form2", instance=obj1)

            context = {"form1": form1, "form2": form2}
            return render(request, "edit_boat.html", context)
        else:
            messages.add_message(request, messages.WARNING, "You can only edit your own entries!",
                                 extra_tags="text-muted  font-weight-bold", fail_silently=True)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


""" Контроллер удаления лодки"""


@method_decorator([login_required_message(message="You must be logged in in order to delete this boat entry"), login_required], name="dispatch")
class BoatDeleteView(DeleteView):
    model = BoatModel
    success_url = reverse_lazy("boats:boats")
    template_name = "delete_boat.html"

    def post(self, request, *args, **kwargs):
        message = 'Boat "%s"  has deleted from the database' % self.get_object().boat_name
        messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True,
                             extra_tags="alert alert-info")
        return DeleteView.post(self, request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return DeleteView.dispatch(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = DeleteView.get_context_data(self, **kwargs)
        if self.user_id:
            context['user'] = ExtraUser.objects.get(pk=self.user_id)
        return context


""" Индекс"""


class IndexPageView(TemplateView):
    template_name = "index.html"


""" список всех лодок"""


class BoatListView(SearchableListMixin, ListView):
    model = BoatModel
    template_name = "boats.html"
    paginate_by = 10
    search_fields = ["boat_name", ]

    def get_ordering(self):
        """метод возвращает поле по которому идет сортировка"""
        self.field = self.request.GET.get('ordering')
        self.mark = self.request.GET.get("mark")
        # if self.field not in [f.name for f in BoatModel._meta.get_fields(include_parents=False)]
        # and self.mark:
        if self.field == '' or self.mark == "":
            messages.add_message(self.request, messages.WARNING, message="Please choose sorting "
                                                                        "pattern", fail_silently=True)
            return None
        if all([self.field, self.mark]):
            self.verbose_name = BoatModel._meta.get_field(self.field).verbose_name
            message = 'Boats are ordered by:\xa0\"' + self.verbose_name + "\"\xa0in\xa0" + \
                      self.mark + "\xa0order"
            if self.field != self.request.COOKIES["ordering"] or \
                    self.mark != self.request.COOKIES["mark"]:
                messages.add_message(self.request, messages.SUCCESS, message=message,
                                     fail_silently=True)
            if self.mark == "descending":
                self.field = "-" + self.field
            return self.field

    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        context["images"] = BoatImage.objects.all().distinct('boat')  # выбирает только 1 уникальный
        # объект из группы объектов с  одинаковым фк, остальные отсеивает
        if self.field and self.mark:
            context["verbose_name"] = self.verbose_name
        return context

    def render_to_response(self, context, **response_kwargs):
        """Для корректного возврата после поиска к отсортированному списку. Сохраняем сортировку в
         куках, а затем извлекаем ее в шаблоне и запихиваем в УРЛ через ГЕТ параметры"""
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
                   :1].iterator()  # i hate "for" cycles within  only one  object in queryset :))
            message = 'Boats are filtered by county "%s"' % next(boat).boat_country_of_origin.name
            messages.add_message(self.request, messages.SUCCESS, message=message, fail_silently=True)
            return qs.filter(boat_country_of_origin=country)
        return qs


""" просмотр  детальной информации о лодке"""


def boat_detail_view(request, pk):
    current_boat = BoatModel.objects.prefetch_related("boatimage_set", "comment_set",
                                                      "article_set").get(pk=pk)
    images = current_boat.boatimage_set.all()
    comments = current_boat.comment_set.all()
    articles = current_boat.article_set.all()
    versions = Version.objects.select_related("revision").get_for_object_reference(BoatModel, pk)
    context = {"images": images, "current_boat": current_boat, "comments": comments,
               "articles": articles, "versions": versions}
    if request.method == "GET":
        return render(request, "boat_detail.html", context)
    else:
        version_num = request.POST.get("rollback")
        if version_num == "":
            messages.add_message(request, messages.WARNING, message="Please choose the rollback point"
                                                                    " date", fail_silently=True)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        elif current_boat.author != request.user:
            messages.add_message(request, messages.WARNING, message="You can only rollback your own"
                                                                    " entries", fail_silently=True)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        return HttpResponseRedirect(reverse_lazy("boats:rollback",  args=(pk, version_num)))


""" Контроллер отката версий лодки"""


class RollbackView(MessageLoginRequiredMixin, DetailView):
    template_name = "rollback.html"
    model = BoatModel
    redirect_message = "You have to be authenticated to rollback boat's data"

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
        # самая старая фотка
        minimal_id = BoatImage.objects.aggregate(min=Min('id', filter=Q(boat_id=self.kwargs["pk"])))
        try:
            context["image"] = BoatImage.objects.get(boat_id=self.kwargs["pk"], pk=minimal_id["min"])
        except ObjectDoesNotExist:
            pass
        return context

    def post(self, request, *args, **kwargs):
        # получаем необходимую версию записи и откатываемся до нее
        version = Version.objects.get(id=self.kwargs["version_id"])
        version.revision.revert()
        #  сайв нужен для привязки /перепривязки категорий статей
        self.get_object().save()
        # если файл  изображения был фактически удален и его путь в бд ведет в никуда то мы его
        # удаляем из БД чтобы пустой путь не был привязан к объекту изображения
        images = self.get_object().boatimage_set.all()
        score = 0
        for image in images:
            if not os.path.exists(image.boat_photo.path):
                image.true_delete(self)  # удаляем по настоящему
                score += 1
        if score != 0:
            message = "%d broken image instances  has been deleted from DB" % score
            messages.add_message(request, messages.WARNING, message=message, fail_silently=True)
        message = "You successfully rolled back %(name)s ` data. Rollback date is %(date)s " % \
                  ({"name": self.get_object().boat_name, "date": version.revision.date_created})
        messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True)
        return HttpResponseRedirect(reverse_lazy('boats:boat_detail', args=(self.kwargs["pk"], )))

    def dispatch(self, request, *args, **kwargs):
        """только автор лодки может делать роллбэк"""
        if self.request.user != self.get_object().author:
            messages.add_message(request, messages.WARNING, "You can only rollback your own entries",
                                 fail_silently=True)
            return self.handle_no_permission()
        return MessageLoginRequiredMixin.dispatch(self, request, *args, **kwargs)


""" Контроллер добавления новой лодки"""


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
            return render(request, "create.html", context)
        if form1.is_valid():
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
            messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True)
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

"""
# альтернативный вариант
@ method_decorator(atomic, name="forms_valid")
class CreateBoatView(LoginRequiredMixin, CreateWithInlinesView):
    model = BoatModel
    inlines = [ItemInline]
    fields = ["boat_name", "boat_length", "boat_mast_type", "boat_keel_type",   "boat_price", "boat_country_of_origin", "boat_sailboatdata_link",  "boat_description"]
    template_name = 'create.html'

    def get_success_url(self):
        return reverse('boats:boat_detail', args=(self.object.pk, ))

    def forms_valid(self, form, inlines):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        form.save(commit=True)
        for formset in inlines:
            formset.save()
            messages.add_message(self.request, messages.SUCCESS,
                                 "Boat has been added", fail_silently=True)
        return HttpResponseRedirect(self.get_success_url())

"""
""" контроллер LOGIN"""


class AdminLoginView(SuccessMessageMixin, LoginView):
    template_name = "admin/login.html"
    success_message = "You have logged in, %(username)s"
    form_class = AuthCustomForm


""" контроллер LOGOUT"""


class AdminLogoutView(LoginRequiredMixin, LogoutView):
    template_name = "admin/logout.html"

    def get(self, request, *args, **kwargs):
        message = "You have logged out"
        messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True)
        logout(request)
        return LogoutView.get(self, request, *args, **kwargs)


""" контроллер страницы профиля пользователя"""


class UserProfileView(LoginRequiredMixin,  TemplateView):
    template_name = "admin/userprofile.html"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context["boats_by_user"] = \
            BoatModel.objects.order_by("-boat_publish_date").filter(author=self.request.user)[: 10]
        context["articles_by_user"] = \
            Article.objects.order_by("created_at").filter(author=self.request.user)[: 10]
        filter1 = Comment.objects.filter(foreignkey_to_article__author=self.request.user,
                                         is_active=True)
        filter2 = Comment.objects.filter(foreignkey_to_boat__author=self.request.user,
                                         is_active=True)
        context["comments_by_user"] = filter1.union(filter2).order_by("-created_at")[: 5]
        return context


""" корректировка данных пользователя"""


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


class PasswordCorrectionView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = "admin/password_change.html"
    success_url = reverse_lazy("boats:user_profile")
    success_message = "Your password has been changed. Please confirm the change " \
                      "via email you will have received shortly "
    form_class = PwdChgForm

    def post(self, request, *args, **kwargs):
        PasswordChangeView.post(self, request, *args, **kwargs)
        logout(request)
        return HttpResponseRedirect(reverse_lazy("boats:user_profile"))


""" добавление нового пользователя"""


class AddNewUserView(CreateView):
    model = ExtraUser
    template_name = "admin/add_new_user.html"
    form_class = NewUserForm
    success_url = reverse_lazy("boats:register_is_done")


"""контроллер успешной регистрации"""


class RegisterDoneView(TemplateView):
    template_name = "admin/register_done.html"


""" контроллер активации пользователя через емейл"""


def user_activate_view(request, sign):  # 575
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, "admin/bad_signature.html")
    user = get_object_or_404(ExtraUser, username=username)
    if user.is_activated:
        template = "admin/user_is_activated.html"
    else:
        template = "admin/successful_activation.html"
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


"""Контроллер удаления зарегестрированного пользователя"""


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
            message = 'Your profile "%s" is successfully deactivated.' % self.request.user.username
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


def feedback_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
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
            form = ContactForm(initial={"sender": auth.get_user(request).email,
                                        "name": auth.get_user(request).username})
        else:
            form = ContactForm()
        context = {"form": form, "username": auth.get_user(request).username}
        return render(request, "feedback.html", context)


""" контроллер отправки письма для сброса пароля"""


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


class PassResConfView(SuccessMessageMixin, PasswordResetConfirmView):
    post_reset_login = True
    post_reset_login_backend = "django.contrib.auth.backends.ModelBackend"
    success_url = reverse_lazy("boats:user_profile")
    success_message = "Dear %(username)s , your password has changed . " \
                      "Please do not forget your new password!"
    template_name = "admin/password_reset_confirmation.html"
    form_class = SPForm


"""контроллер рендеринга в PDF  в поток"""


class Pdf(TemplateView):
    def get(self, request, *args, **kwargs):
        pr = Prefetch("boatimage_set", to_attr="images")
        current_boat = BoatModel.objects.prefetch_related(pr).get(pk=self.kwargs["pk"])
        params = {"current_boat": current_boat, "request": request}
        return Render.render("pdf/pdf.html", params, filename=current_boat.boat_name)  # см.                                                                                            .render.py


"""контроллер рендеринга в PDF  в файл"""


def render_pdf_view(request, pk):
    template_path = "pdf/pdf.html"
    pr = Prefetch("boatimage_set", to_attr="images")
    current_boat = BoatModel.objects.prefetch_related(pr).get(pk=pk)
    context = {"current_boat": current_boat, "request": request}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % (current_boat.boat_name + ".pdf")

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


class ReversionView(MessageLoginRequiredMixin, TemplateView):
    template_name = "reversion.html"
    redirect_message = "You need to be authenticated to recover boat's data"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        # pk всех существующих  в базе лодок
        existing_boats_pk = BoatModel.objects.all().values_list("pk", flat=True).iterator()
        #  Выбираем все удаленные лодки текущим пользователем
        versions = Version.objects.get_for_model(BoatModel).filter(
            Q(revision__user_id=self.request.user.id) | Q(revision__user_id__isnull=True)).exclude(
            object_id__in=existing_boats_pk).order_by("object_id").distinct("object_id")
        context["versions"] = versions
        # фото всех удаленных лодок
        images = BoatImage.objects.filter(boat_id__isnull=True).exclude(memory__in=existing_boats_pk)
        # список рк всех фоток не привязанных к лодкам
        images.memory_list = str(images.values_list("memory", flat=True))
        for image in images:
            image.memory = str(image.memory)
        context["images"] = images
        return context


""" Контроллер восстановления конкретной лодки"""


@login_required_message(message="You need to be authenticated to recover boat's data")
@login_required
def reversion_confirm_view(request, pk):
    versions = Version.objects.get_for_model(BoatModel).filter(object_id=pk)[0:1]
    if request.method == "POST":
        versions[0].revision.revert()
        restored_boat = BoatModel.objects.get(boat_name=versions[0].object_repr)
        restored_boat.save()
        message = 'Boat "%(boat_name)s" is restored!' % {"boat_name": versions[0].object_repr}
        messages.add_message(request, messages.SUCCESS, message=message, fail_silently=True)
        return HttpResponseRedirect(reverse_lazy("boats:boat_detail",  args=(pk, )))
    else:
        context = {"versions": versions}
        return render(request, "reversion_confirmation.html", context)
