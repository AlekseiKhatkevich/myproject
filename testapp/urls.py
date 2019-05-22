from django.contrib import admin
from django.urls import path
from .views import *

app_name = 'testapp'
urlpatterns = [
    #FBV
    path('', contactPage, name="contact_page"),
    path('ajax/contact/', postContact, name='contact_submit'),
    path("cbw/", ContactAjax.as_view(), name='contact_submit_cbw'),
]
