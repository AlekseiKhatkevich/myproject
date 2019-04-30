from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django_countries.widgets import CountrySelectWidget
from .models import *
from django.forms import inlineformset_factory
from captcha.fields import CaptchaField, CaptchaTextInput
from extra_views import InlineFormSetFactory
from django.core.validators import MinValueValidator
import datetime
from. widgets import *
import requests
from django.core.exceptions import ObjectDoesNotExist

""" форма лодки"""


def year_choices():
    return [(r, r) for r in range(1950, datetime.date.today().year + 1)]


class BoatForm(forms.ModelForm):
    boat_length = forms.FloatField(min_value=10, help_text="Please input boat water-line length",)
    boat_price = forms.IntegerField(help_text="Please input boat price",
        validators=[validators.MinValueValidator(5000, message="Are you sure? It is almost free!",)])
    first_year = forms.TypedChoiceField(coerce=int, choices=year_choices,
                                    help_text="Please enter first manufacturing year of the model")
    last_year = forms.TypedChoiceField(coerce=int, choices=year_choices,
                                    help_text="Please enter last manufacturing year of the model")

    class Meta:
        model = BoatModel
        fields = ("boat_name", "boat_length", "boat_mast_type", "boat_keel_type",   "boat_price",
                  "boat_country_of_origin", "boat_sailboatdata_link",  "boat_description",
                  "first_year", "last_year")
        widgets = {"boat_country_of_origin": CountrySelectWidget(layout='{widget}<img  class="country-select-flag" id="{flag_id}" style="margin: 6px 4px 0; width: 45px; height: 26px;  " src="{country.flag}">')}

    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        first_year = int(cleaned_data.get("first_year"))
        last_year = int(cleaned_data.get("last_year"))

        if first_year > last_year and first_year and last_year:
            msg = 'Last year has to be superior then first year'
            self.add_error("last_year", msg)

        # проверяет живой ли урл и , что урл веден на 'sailboatdata.com'
    def clean_boat_sailboatdata_link(self):
        msg3 = "This URL does not work!"
        msg4 = "Please provide url exactly to 'sailboatdata.com' "
        msg5 = "Connection error"
        url = self.cleaned_data["boat_sailboatdata_link"]
        try:
            request = requests.head(url)
            if request.status_code // 100 != 2:
                self.add_error("boat_sailboatdata_link", msg3)
            elif "sailboatdata.com" not in url:
                self.add_error("boat_sailboatdata_link", msg4)
        except requests.exceptions.ConnectionError:
            self.add_error("boat_sailboatdata_link", msg5)
        return url


"""форма доп. изображений лодки"""


class BoatImageForm(forms.ModelForm):
    class Meta:
        model = BoatImage
        fields = ("boat_photo", )


"""формсет связанный с вторичной моделью"""


boat_image_inline_formset = inlineformset_factory(BoatModel, BoatImage,  fields=("boat_photo", ),
extra=3, can_delete=True, max_num=10, widgets={"boat_photo": CustomKeepImageWidget()}, labels={"boat_photo": None})


"""
#  альтернативный вариант
class ItemInline(InlineFormSetFactory):
    model = BoatImage
    fields = ["boat_photo"]
    factory_kwargs = {'extra': 4, 'max_num': None,
                      'can_order': False, 'can_delete': True}
"""

"""Форма коректировки пользователя"""


class CorrectUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Your email address')

    class Meta:
        model = ExtraUser
        fields = ("username", "email", "first_name", "last_name", )


""" Form for a new user registration"""


class NewUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Your email address",
                             help_text="Please input your email address")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(render_value=True),
                                help_text=password_validation.password_validators_help_text_html(), )
    password2 = forms.CharField(label="Confirm your password", widget=forms.PasswordInput(
        render_value=True), help_text="Please input password again", )
    captcha = CaptchaField()

    def clean_password1(self):
        password1 = self.cleaned_data["password1"]
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        forms.ModelForm.clean(self)
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]
        if password1 and password2 and password1 != password2:
            errors = {"password2": ValidationError("Passwords aren't coincide!",                                                                                                    code="password_mismatch")}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = forms.ModelForm.save(self, commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
            user_registrated.send(NewUserForm, instance=user)  # сигнал
            return user

    class Meta:
        model = ExtraUser
        fields = ("username", 'email', "password1", "password2", "first_name", "last_name")


""" форма обратной связи"""


class ContactForm(forms.Form):
    attrs_dict = {'size': 40, "class": "form-control  border border-secondary"}

    name = forms.CharField(max_length=20, help_text="Enter your name",
                           widget=forms.TextInput(attrs=attrs_dict))
    subject = forms.CharField(max_length=999, help_text="Enter  a subject of the message",
                              widget=forms.TextInput(attrs=attrs_dict))
    sender = forms.EmailField(help_text="Enter your email address",
                              widget=forms.TextInput(attrs=attrs_dict))
    message = forms.CharField(help_text="please type in your message",
                              widget=forms.Textarea(attrs=attrs_dict))
    copy = forms.BooleanField(required=False, label="Send copy to your email")
    captcha = CaptchaField(help_text="Please type in correct captcha",
                           widget=CaptchaTextInput(attrs=attrs_dict))


"""кастомная форма сброса пароля(первая часть)"""


class PRForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not ExtraUser.objects.filter(email__iexact=email).exists():
            msg = "There is no user registered with the specified E-Mail address."
            self.add_error('email', msg)
        elif ExtraUser.objects.filter(email__iexact=email, is_active=False).exists():
            msg = "This account had been deactivated or wasn't activated at all."
            self.add_error('email', msg)
        else:
            current_user = ExtraUser.objects.get(email__iexact=email, is_active=True, is_activated=True)
            if current_user:
                self.cleaned_data["username"] = current_user
        return email


"""кастомная форма сброса пароля(вторая часть)"""


class SPForm(SetPasswordForm):
    def clean(self):
        if self.user.username:
            self.cleaned_data["username"] = self.user.username
        else:
            self.cleaned_data["username"] = "Anonymous user"
        SetPasswordForm.clean(self)


""" форма для смены пароля - отправляет письмо для подтверждения активации смены пароля"""


class PwdChgForm(PasswordChangeForm):

    def save(self, commit=True):
        self.user.is_activated = False
        self.user.is_active = False
        user_registrated.send(PwdChgForm, instance=self.user)
        PasswordChangeForm.save(self, commit=True)


""" Кастомная форма для лог-ина. Предупреждает неактивированного юзера, что акаун не активированн"""


class AuthCustomForm(AuthenticationForm):

    def get_invalid_login_error(self):
        users = ExtraUser.objects.filter(username=self.cleaned_data.get('username'))
        for user in users:
            if not user.is_active and user:
                raise forms.ValidationError(
                    "Account '%(value)s' has been deactivated or wasn't activated at all",
                    code='inactive',
                    params={'value': user})
        else:
            return forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name, },
            )


