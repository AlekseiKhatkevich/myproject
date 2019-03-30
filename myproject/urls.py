from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls.static import static
from .settings import DEBUG, MEDIA_URL, MEDIA_ROOT
from django.contrib. staticfiles.views import serve
from django.views.decorators.cache import never_cache

urlpatterns = [
    path('admin/', admin.site.urls ),
    path("articles/", include("articles.urls")),
    path("", include("boats.urls")),
]

if DEBUG:
    urlpatterns.append(path("static/<path:path>", never_cache(serve)))
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)


