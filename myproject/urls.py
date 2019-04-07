from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls.static import static
from .settings import DEBUG, MEDIA_URL, MEDIA_ROOT
from django.contrib. staticfiles.views import serve
from django.views.decorators.cache import never_cache
from django.views.defaults import permission_denied
from django.utils.functional import curry

urlpatterns = [
    path("social/", include('social_django.urls', namespace='social')),
    path("captcha/", include("captcha.urls")),
    path('admin/', admin.site.urls),
    path("articles/", include("articles.urls")),
    path("", include("boats.urls")),
]

if DEBUG:
    urlpatterns.append(path("static/<path:path>", never_cache(serve)))
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)


handler403 = curry(permission_denied, exception=Exception('Permission Denied'), template_name='errors/403.html')
#handler404 = curry(page_not_found, exception=Exception('Page not Found'), template_name='errщкs/404.html')
