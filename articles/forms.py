from .models import *
from django import forms
from django.shortcuts import get_object_or_404
import requests
from django.db.models import Q, F

"""search form"""


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label="")


""" Форма добавления статьи"""


class ArticleForm(forms.ModelForm):

    def clean_foreignkey_to_boat(self):
        # в случае, если мы сохраняем статью  в категории "Articles on boats" то проверяется была ли выбрана связанная со статьей лодка.
        foreignkey_to_boat = self.cleaned_data["foreignkey_to_boat"]
        foreignkey_to_subheading = int(self.cleaned_data["foreignkey_to_subheading"].pk)
        current_subheading = get_object_or_404(SubHeading, pk=foreignkey_to_subheading)
        if current_subheading.foreignkey.name == "Articles on boats" and not foreignkey_to_boat:
            msg1 = 'You must choose the boat if you want to save this article inside upper heading' \
                  ' "Articles on boats"'
            self.add_error("foreignkey_to_boat", msg1)
        # проверяем совпадают ли имена подкатегории и название лодки, если мы пытаемся сохранитьстатью в категории "Articles on boats"
        if current_subheading.foreignkey.name == "Articles on boats" and foreignkey_to_boat and\
                foreignkey_to_boat.boat_name != current_subheading.name:
            msg2 = 'Name of the boat should coincide to the sub-heading name '
            self.add_error("foreignkey_to_boat", msg2)
        return foreignkey_to_boat

    # проверяет живой ли урл
    def clean_url_to_article(self):
        msg3 = "This URL does not work!"
        msg4 = "Connection error"
        url = self.cleaned_data["url_to_article"]
        try:
            request = requests.head(url)
            if request.status_code // 100 != 2:
                self.add_error("url_to_article", msg3)
        except requests.exceptions.ConnectionError:
            self.add_error("url_to_article", msg4)
        return url

    class Meta:
        model = Article
        exclude = ("created_at", "show", "change_date" )
        widgets = {"author": forms.HiddenInput, }


"""Форма комментов статьи  и лодки"""


class ArticleCommentForm(forms.ModelForm):
    captcha = CaptchaField(label=" Captcha", help_text="Please type in captcha", error_messages={"invalid": "wrong captcha"})

    def __init__(self,  *args, **kwargs):
        self.author = kwargs.pop("author", None)
        forms.ModelForm.__init__(self, *args, **kwargs)
        # подключение Popover в форме
        for field in self.fields:   # нужен javascript
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'right',
                     'data-container': 'body'})
        #  у активированного пользователя отключаем возможность редактирования поля имени
        if self.author:
            self.fields["author"].disabled = True

    class Meta:
        model = Comment
        exclude = ("is_active", )
        widgets = {"foreignkey_to_boat": forms.HiddenInput, "foreignkey_to_article": forms.HiddenInput}


"""форма ап-категории для добавления"""


class UpperHeadingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.pk = kwargs.pop("pk", None)
        forms.ModelForm.__init__(self, *args, **kwargs)
        if self.pk != 0:
            self.fields["name"].widget = forms.HiddenInput()
        for field in self.fields:   # нужен javascript
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'right',
                     'data-container': 'body'})

    class Meta:
        model = UpperHeading
        fields = ("name", )
        labels = {"name": "New upper heading", }
        help_texts = {"name": "Please type in name of the new upper heading"}


"""форма суб категории для добавления"""


class SubHeadingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.pk = kwargs.pop("pk", None)
        forms.ModelForm.__init__(self, *args, **kwargs)
        for field in self.fields:   # нужен javascript
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover', 'data-content': help_text, 'data-placement': 'right',
                     'data-container': 'body'})

    class Meta:
        model = SubHeading
        exclude = ("foreignkey", "one_to_one_to_boat")
        labels = {"name": "Sub heading name"}
        help_texts = {"name": "Please type in name of the new sub-heading",
                      "order": "Order of the sub-headings in the headings category"}


"""Форма восстановления статей"""


class CustomM2MChoiceFiled(forms.ModelMultipleChoiceField):
    """слегка кастомизированное поле"""
    # https://docs.djangoproject.com/en/dev/ref/forms/fields/#django.forms.ModelChoiceField
    def label_from_instance(self, obj):
        """ возвращаем человеческий плесхолдер для формы"""
        return "//DELETED// %s, title - '%s', created - %s \xa0 %s, deleted - %s \xa0 %s" % (
            obj.foreignkey_to_subheading, obj.title,  obj.created_at.date(), obj.created_at.ctime()
            [11:-4], obj.change_date.date(), obj.change_date.ctime()[11:-4])


class ArticleResurrectionForm(forms.ModelForm):

    pk = CustomM2MChoiceFiled(label="Deleted articles:", queryset=Article.default.none(),
    help_text="Please select the articles to recover (you can select multiple articles by using shift "
              "or crtl )")
    #  https://stackoverflow.com/questions/56099703/pass-request-user-into-form-with
    #  -modelmultiplechoicefield-django/56099757#56099757

    def __init__(self, *args, **kwargs):
        author_id = kwargs.pop("author_id", None)
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields["pk"].queryset = Article.default.select_related(
            "foreignkey_to_subheading").filter(author_id=author_id, show=False,).order_by(
            "-created_at")

    def clean(self):
        """Восстанавливаем статьи методом перевода show  в True"""
        forms.ModelForm.clean(self)
        pk_list = self.cleaned_data["pk"]
        Article.default.filter(id__in=pk_list).update(show=True)

    class Meta:
        model = Article
        fields = ("pk", )



