from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages, auth
from .utilities import signer
from django.core.signing import BadSignature
from .models import *
from .forms import *
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.db.transaction import atomic
from django.core.mail import send_mail, BadHeaderError


"""Контроллер редактирования данных о лодке"""


@atomic
@login_required
def viewname_edit(request, pk):
    obj1 = BoatModel.objects.get(pk=pk)
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1", instance=obj1)
        form2 = boat_image_inline_formset(request.POST, request.FILES, prefix="form2", instance=obj1)
        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()
            messages.add_message(request, messages.SUCCESS, "You successfully edited boat's data")
            return HttpResponseRedirect(reverse_lazy("boats:boat_detail", args=(pk, )))
        else:
            messages.add_message(request, messages.WARNING, "Forms are not valid. Please check the data")
            context = {"form1": form1, "form2": form2}
            return render(request, "edit_boat.html", context)
    else:
        if request.user == obj1.author:
            form1 = BoatForm(prefix="form1", instance=obj1)
            form2 = boat_image_inline_formset(prefix="form2", instance=obj1)
            context = {"form1": form1, "form2": form2}
            return render(request, "edit_boat.html", context)
        else:
            messages.add_message(request, messages.WARNING, "You can only change your own entries!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# не используется
class BoatUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = BoatModel
    template_name = "edit_boat.html"
    form_class = BoatForm
    success_message = "Boat data has been edited and saved successfully"

    def get(self, request, *args, **kwargs):
        if self.get_object().author == self.request.user:
            return UpdateView.get(self, request, *args,  **kwargs)
        else:
            messages.add_message(request, messages.WARNING, "You can only change your own entries!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def get_success_url(self):
        return reverse('boats:boat_detail', args=(self.object.pk, ))


""" контроллер удаления лодки"""


#  todo  кнопки руский шрифт в форме
@ method_decorator(login_required, name="dispatch")
class BoatDeleteView(DeleteView):
    model = BoatModel
    success_url = reverse_lazy("boats:boats")
    template_name = "delete_boat.html"

    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, "Boat has deleted from the database")
        return DeleteView.post(self, request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return DeleteView.dispatch(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = DeleteView.get_context_data(self, **kwargs)
        context['user'] = ExtraUser.objects.filter(pk=self.user_id)
        return context


class TestView(TemplateView):
    template_name = "newtemplate.html"


""" Индекс"""


class IndexPageView(TemplateView):
    template_name = "index.html"


""" список всех лодок"""


def boat_view(request):
    boats = BoatModel.objects.all()
    images = BoatImage.objects.all()
    context = {"boats": boats, "images": images}
    return render(request, "boats.html", context)


""" просмотр  детальной информации о лодке"""


#
def boat_detail_view(request, pk):
    current_boat = BoatModel.objects.get(pk=pk)  # primary
    images = current_boat.boatimage_set.all()
    context = {"images": images, "current_boat": current_boat}
    return render(request, "boat_detail.html", context)


""" Контроллер добавления новой лодки"""


@atomic
@login_required
def viewname(request):
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1")
        form2 = boat_image_inline_formset(request.POST, request.FILES, prefix="form2", )
        if form1.is_valid():
            prim = form1.save(commit=False)
            prim.author = request.user
            form1.save()
            form2 = boat_image_inline_formset(request.POST, request.FILES,
                                              prefix="form2", instance=prim)
            if form2.is_valid():
                form2.save()
                messages.add_message(request, messages.SUCCESS, "You added a new boat")
                return HttpResponseRedirect(reverse_lazy("boats:boat_detail",
                                                     args=(prim.pk, )))
        else:
            messages.add_message(request, messages.WARNING, "Forms are not valid. Please check the data")
            context = {"form1": form1, "form2": form2}
            return render(request, "create.html", context)
    else:

        form1 = BoatForm(prefix="form1")
        form2 = boat_image_inline_formset(request.POST or None, request.FILES or None, prefix="form2", )
        context = {"form1": form1, "form2": form2}
        return render(request, "create.html", context)


""" контроллер LOGIN"""


class AdminLoginView(SuccessMessageMixin, LoginView):
    template_name = "admin/login.html"
    success_message = "You have logged in"


""" контроллер LOGOUT"""


# @login required
class AdminLogoutView(LoginRequiredMixin, LogoutView):
    template_name = "admin/logout.html"
    success_message = "You have logged out"

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, "You have logged out")
        return LogoutView.get(self, request, *args, **kwargs)


""" контроллер страницы профиля пользователя"""


# @login required
class UserProfileView(LoginRequiredMixin,  TemplateView):
    template_name = "admin/userprofile.html"


""" корректировка данных пользователя"""


# @login required
class CorrectUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):  #  566, 205
    model = ExtraUser
    template_name = "admin/correct_user_info.html"
    form_class = CorrectUserInfoForm
    success_url = reverse_lazy("boats:user_profile")
    success_message = "Your personal data has been corrected"

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return UpdateView.dispatch(self, request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


""" Изменение пароля"""


# @login required
class PasswordCorrectionView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = "admin/password_change.html"
    success_url = reverse_lazy("boats:user_profile")
    success_message = "your password has been changed"


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


#   @login required
class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = ExtraUser
    template_name = 'admin/delete_user.html'
    success_url = reverse_lazy("boats:index")

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return DeleteView.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, "your account is deleted")
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
                                     "You have successfully sent your  message to the administration ")
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
