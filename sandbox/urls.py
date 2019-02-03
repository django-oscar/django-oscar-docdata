from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from oscar_docdata.dashboard.app import application as docdata_dashboard_app

from oscar.app import application as oscar_application

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Include docdata URLs
    url(r'^dashboard/docdata/', docdata_dashboard_app.urls),
    url(r'^api/docdata/', include('oscar_docdata.urls')),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'', oscar_application.urls),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
