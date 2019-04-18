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

    class Meta:
        model = Article
        exclude = ("created_at", )
        widgets = {"author": forms.HiddenInput, }


"""Форма комментов статьи  и лодки"""


class ArticleCommentForm(forms.ModelForm):
    captcha = CaptchaField(label=" Captcha", help_text="Please type in captcha", error_messages={"invalid": "wrong captcha"})

    def __init__(self, key, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        """
        if key == "article":
            self.fields["foreignkey_to_boat"].widget = forms.HiddenInput()
        else:
            self.fields["foreignkey_to_article"].widget = forms.HiddenInput()
            """
        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'right',
                     'data-container': 'body'})

    class Meta:
        model = Comment
        exclude = ("is_active", )
        widgets = {"foreignkey_to_boat": forms.HiddenInput, "foreignkey_to_article": forms.HiddenInput}



