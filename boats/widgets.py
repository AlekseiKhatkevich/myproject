from django.forms.widgets import ClearableFileInput


class CustomClearableFileInput(ClearableFileInput):
    template_name = 'customclearablefileinput.html'
    #template_name = "trash/original.html"
