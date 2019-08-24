from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import Token
from reversion.admin import VersionAdmin


#@admin.register(Token)
class TokeAdmin(VersionAdmin):
    """Админ RestAPI AUTH-token"""
    pass
