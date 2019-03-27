from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy


class ArticlesMainView(TemplateView):
    template_name = "articles/articles_index.html"
