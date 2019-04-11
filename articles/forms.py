from .models import *
from django import forms

"""Форма поля выбора ап-группы,обязательное к заполнению"""


class SubHeadingForm(forms.ModelForm):
    upper_heading = forms.ModelChoiceField(queryset=UpperHeading.objects.all(),
                                           empty_label=None, label="Upper Heading", required=True)

    class Meta:
        model = SubHeading
        fields = '__all__'


"""search form"""


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label="")


