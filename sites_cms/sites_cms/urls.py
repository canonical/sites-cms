from django.conf import settings
from django.urls import include, path
from django.views.generic import RedirectView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from core import views as core_views

urlpatterns = [
    path("_status/check", core_views.status_check, name="status_check"),
    path("robots.txt", core_views.robots_txt, name="robots_txt"),
    # This service has no public pages: send visitors to the admin.
    path("", RedirectView.as_view(url="/admin/"), name="root"),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

# Wagtail's page routes must come last. The admin needs them to work out
# page addresses even though nothing public is served from here.
urlpatterns += [path("", include(wagtail_urls))]
