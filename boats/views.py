from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
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
from django.db.models import Prefetch
from django.core.mail import send_mail, BadHeaderError
from ratelimit.mixins import RatelimitMixin
from extra_views import CreateWithInlinesView
from django.db.models import Q
from .decorators import login_required_message, MessageLoginRequiredMixin
from .render import Render, link_callback
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa


"""Контроллер редактирования данных о лодке"""


@atomic
@login_required_message(message="You must be logged in in order to edit this boat entry")
@login_required
def viewname_edit(request, pk):
    obj1 = BoatModel.objects.get(pk=pk)
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1", instance=obj1)
        form2 = boat_image_inline_formset(request.POST, request.FILES, prefix="form2", instance=obj1)
        if form1.is_valid() and form2.is_valid():
            if form1.has_changed() or form2.has_changed():
                form1.save()
                form2.save()
                messages.add_message(request, messages.SUCCESS,
                                 "You successfully edited boat's data", fail_silently=True)
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
        messages.add_message(request, messages.SUCCESS,
                             "Boat  has deleted from the database", fail_silently=True,
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


class BoatListView(ListView):
    model = BoatModel
    template_name = "boats.html"
    paginate_by = 10

    def get_ordering(self):  # метод возвращает поле по которому идет сортировка
        self.field = self.request.GET.get('ordering')
        self.mark = self.request.GET.get("mark")
        if self.field not in (f.name for f in BoatModel._meta.get_fields()) and self.mark:
            messages.add_message(self.request, messages.WARNING, message="Please choose sorting pattern",
                                 fail_silently=True)
            return None
        if all([self.field, self.mark]):
            verbose_name = BoatModel._meta.get_field(self.field).verbose_name
            message = 'Boats are ordered by:\xa0\"' + verbose_name + "\"\xa0in\xa0" + \
                      self.mark + "\xa0order"
            messages.add_message(self.request, messages.SUCCESS, message=message, fail_silently=True)
            if self.mark == "descending":
                self.field = "-" + self.field
            return self.field
        return None


""" просмотр  детальной информации о лодке"""


def boat_detail_view(request, pk):
    current_boat = BoatModel.objects.get(pk=pk)
    images = current_boat.boatimage_set.all()
    comments = current_boat.comment_set.all()
    articles = current_boat.article_set.all()
    context = {"images": images, "current_boat": current_boat, "comments": comments, "articles":
        articles}
    return render(request, "boat_detail.html", context)


""" Контроллер добавления новой лодки"""


@atomic
@login_required_message(message="You must be logged in in order to create new boat entry")
@login_required
def viewname(request):
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1")
        if form1.is_valid():
            prim = form1.save(commit=False)
            prim.author = request.user
            form2 = boat_image_inline_formset(request.POST, request.FILES,
                                              prefix="form2", instance=prim)
        else:
            form2 = boat_image_inline_formset(request.POST, request.FILES, prefix="form2")
            context = {"form1": form1, "form2": form2}
            return render(request, "create.html", context)
        if form2.is_valid():
            form1.save()
            form2.save()
            messages.add_message(request, messages.SUCCESS, "You added a new boat")
            return HttpResponseRedirect(reverse_lazy("boats:boat_detail",
                                                     args=(prim.pk, )))
        else:
            form2 = boat_image_inline_formset(request.POST, request.FILES,
                                              prefix="form2", instance=prim)
            context = {"form1": form1, "form2": form2}
            return render(request, "create.html", context)
    else:
        form1 = BoatForm(prefix="form1")
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
        logout(request)
        messages.add_message(request, messages.SUCCESS, "You have logged out", fail_silently=True)
        return LogoutView.get(self, request, *args, **kwargs)


""" контроллер страницы профиля пользователя"""


class UserProfileView(LoginRequiredMixin,  TemplateView):
    template_name = "admin/userprofile.html"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context["boats_by_user"] = \
            BoatModel.objects.order_by("boat_publish_date").filter(author=self.request.user)[: 10]
        context["articles_by_user"] = \
            Article.objects.order_by("created_at").filter(author=self.request.user)[: 10]
        filter1 = Comment.objects.filter(foreignkey_to_article__author=self.request.user,
                                         is_active=True)
        filter2 = Comment.objects.filter(foreignkey_to_boat__author=self.request.user,
                                         is_active=True)
        context["comments_by_user"] = filter1.union(filter2).order_by("-created_at")[: 5]
        """ context["comments_by_user"] = Comment.objects.filter(Q(
            foreignkey_to_article__author=self.request.user) | Q(
            foreignkey_to_boat__author=self.request.user), is_active=True)
            .order_by("-created_at")[:5]"""
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
    success_message = "your password has been changed. Please confirm the change " \
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
            messages.success(request, 'Your profile is '
                                      'successfully disabled.', fail_silently=True)
            logout(self.request)
            return HttpResponseRedirect(reverse_lazy("boats:index"))
        else:
            logout(request)
            messages.add_message(request, messages.SUCCESS,
                                 "Your account is deleted", fail_silently=True)
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
        return Render.render("pdf/pdf.html", params)  # см. .render.py


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
