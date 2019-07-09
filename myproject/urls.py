from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib. staticfiles.views import serve
from django.views.decorators.cache import never_cache
from django.views.defaults import permission_denied, page_not_found, server_error
from django.utils.functional import curry
from django.conf import settings
from django.conf.urls import url


urlpatterns = [
    path("social/", include('social_django.urls', namespace='social')),
    path("captcha/", include("captcha.urls")),
    path('admin/', admin.site.urls),
    path("articles/", include("articles.urls")),
    path("", include("boats.urls")),
    url(r'fancy-cache', include('fancy_cache.urls')),
    path("api/", include("api.urls")),
]

# для отдачи статики в дебаг = фалс ---manage.py runserver --insecure
if settings.DEBUG:
    urlpatterns.append(path("static/<path:path>", never_cache(serve)))  # если не загр. картинки то смотреть сюда
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))

# обработчик 403 ошибки(Access denied)
handler403 = curry(permission_denied, exception=Exception('Permission Denied'),
                   template_name='errors/403.html')
# обработчик 404 ошибки(Not Found)
handler404 = curry(page_not_found, exception=Exception('Page not Found'),
                   template_name='errors/404.html')

# названия для админки
admin.site.site_header = "Boat's project  Admin"
admin.site.site_title = "BOATS Admin Portal"
admin.site.index_title = "BOATS administration page"

