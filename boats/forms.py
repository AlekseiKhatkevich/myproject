from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .models import *


class BoatForm(forms.ModelForm):
    class Meta:
        model = BoatModel
        fields = ("boat_name", "boat_length", "boat_mast_type", "boat_keel_type", "boat_primary_photo",  "boat_price", "boat_country_of_origin", "boat_sailboatdata_link", "boat_primary_photo", "boat_description")


class BoatImageForm(forms.ModelForm):
    class Meta:
        model = BoatImage
        fields = ("boat_photo", )


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
    password2 = forms.CharField(label="Confirm your password", widget=forms.PasswordInput(render_value=True),
                                help_text="Please input password again", )

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
            errors = {"password2": ValidationError("Passwords aren't coincide!", code="password_mismatch")}
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


"""search form"""


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label="")




