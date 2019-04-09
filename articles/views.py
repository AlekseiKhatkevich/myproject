from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import *

"""контроллер гл. стр. артиклес"""


class ArticlesMainView(TemplateView):
    template_name = "articles/articles_index.html"


def show_by_heading_view(request, pk):
    pass
