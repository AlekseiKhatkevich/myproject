from .models import *
from django import forms
from django.forms.widgets import Select

"""Форма поля выбора ап-группы (для админки),обязательное к заполнению"""


class SubHeadingForm(forms.ModelForm):
    upper_heading = forms.ModelChoiceField(queryset=UpperHeading.objects.all(),
                                           empty_label=None, label="Upper Heading", required=True)

    class Meta:
        model = SubHeading
        fields = '__all__'


"""search form"""


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label="")


""" Форма добавления статьи"""


class ArticleForm(forms.ModelForm):
    #foreignkey_to_subheading = forms.ModelChoiceField(empty_label=None, queryset=SubHeading.objects.all(), label="Heading and subheading category",
                                   # help_text="Please choose subheading")

    class Meta:
        model = Article
        exclude = ("created_at", )
        widgets = {"author": forms.HiddenInput, }
