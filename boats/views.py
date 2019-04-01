from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from .utilities import signer
from django.core.signing import BadSignature
from django.contrib.auth import logout
from django.contrib import messages
from .models import *
from .forms import *
from django.http import Http404, HttpResponseRedirect
from django.utils.decorators import method_decorator

"""Контроллер редактирования данных о лодке"""

# todo redirect,  multiple objects
@login_required
def viewname_edit(request, pk):
    obj1 = BoatModel.objects.get(pk=pk)
    obj2 = BoatImage.objects.get(boat_id=pk)  # множественные объекты???
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1", instance=obj1)
        form2 = BoatImageForm(request.POST, request.FILES, prefix="form2", instance=obj2)
        if form1.is_valid() and form2.is_valid():
            prim = form1.save()
            second = form2.save(commit=False)
            second.boat = prim
            second.save()
            messages.add_message(request, messages.SUCCESS, "You successfully edited a  boat's data")
            return HttpResponseRedirect(reverse_lazy("boats:boat_detail", args=(pk, )))

        else:
            messages.add_message(request, messages.WARNING, "Forms are not valid. Please check the data")
            context = {"form1": form1, "form2": form2}
            return render(request, "edit_boat.html", context)
    else:
        if request.user == obj1.author:
            form1 = BoatForm(prefix="form1", instance=obj1)
            form2 = BoatImageForm(prefix="form2", instance=obj2)
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


# todo формсет
def boat_detail_view(request, pk):
    current_boat = BoatModel.objects.get(pk=pk)  # primary
    images = current_boat.boatimage_set.all()
    context = {"images": images, "current_boat": current_boat}
    return render(request, "boat_detail.html", context)


""" Контроллер добавления новой лодки"""

# todo перенаправление на только что созданное объявление
@login_required
def viewname(request):
    if request.method == 'POST':
        form1 = BoatForm(request.POST, request.FILES, prefix="form1")
        form2 = BoatImageForm(request.POST, request.FILES, prefix="form2")
        if form1.is_valid() and form2.is_valid():
            prim = form1.save(commit=False)
            prim.author = request.user
            prim.save()
            second = form2.save(commit=False)
            second.boat = prim
            second.save()
            messages.add_message(request, messages.SUCCESS, "you added a new boat")
            return redirect(reverse_lazy("boats:boats",
                                                     args=form1.cleaned_data["pk"]))
    else:
        form1 = BoatForm(prefix="form1")
        form2 = BoatImageForm(prefix="form2")
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

