from django.forms.widgets import ClearableFileInput
from file_resubmit.admin import AdminResubmitImageWidget
from django import forms

""" виджет для загрузки фоток """


class CustomClearableFileInput(ClearableFileInput):
    template_name = 'customclearablefileinput.html'
    #template_name = "trash/original.html" - original template


""" виджет для загрузки фоток  с сохранением файлов при перезагрузке"""


class CustomKeepImageWidget(AdminResubmitImageWidget):
    template_name = 'customclearablefileinput.html'
    #  https://stackoverflow.com/questions/3097982/how-to-make-a-django-form-retain-a-file-after-failing
    #  -validation

    def output_extra_data(self, value):
        output = ''
        #if value and self.cache_key:
            #output += ' ' + self.filename_from_value(value)  # выводит имя файла под полем
        if self.cache_key:
            output += forms.HiddenInput().render(
                self.input_name,
                self.cache_key,
                {},
            )
        return output

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({"filename": self.filename_from_value(value)})
        return context
