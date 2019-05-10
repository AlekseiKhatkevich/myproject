from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls.static import static
from .settings import DEBUG, MEDIA_URL, MEDIA_ROOT, INSTALLED_APPS
from django.contrib. staticfiles.views import serve
from django.views.decorators.cache import never_cache
from django.views.defaults import permission_denied
from django.utils.functional import curry
from django.conf import settings
from django.conf.urls import  url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

"""
admin.autodiscover()

i18n_urls = (  #  new
    path('admin/', admin.site.urls),  # может быть конфликт с админом ниже
    path('i18n/', include('django.conf.urls.i18n')),
)
"""


urlpatterns = [
    path("social/", include('social_django.urls', namespace='social')),
    path("captcha/", include("captcha.urls")),
    path('admin/', admin.site.urls),
    path("articles/", include("articles.urls")),
    path("", include("boats.urls")),
]

if DEBUG:
    urlpatterns.append(path("static/<path:path>", never_cache(serve)))  # если не загр. картинки то смотреть сюда
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
    if "debug_toolbar" in INSTALLED_APPS:
        import debug_toolbar
        urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))

# обработчик 403 ошибки(Access denied)
handler403 = curry(permission_denied, exception=Exception('Permission Denied'), template_name='errors/403.html')
#handler404 = curry(page_not_found, exception=Exception('Page not Found'), template_name='errors/404.html')

# названия для админки
admin.site.site_header = "Boat's project  Admin"
admin.site.site_title = "BOATS Admin Portal"
admin.site.index_title = "BOATS administration page"
"""
# new
urlpatterns.extend(i18n_patterns(*i18n_urls, prefix_default_language=False))
urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
"""
