from __future__ import unicode_literals

from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views.i18n import set_language

from mezzanine.pages import views as pages_view
from mezzanine.core.views import direct_to_template
from mezzanine.conf import settings

admin.autodiscover()

urlpatterns = i18n_patterns(
    url("^admin/", include(admin.site.urls)),
)

if settings.USE_MODELTRANSLATION:
    urlpatterns += [
        url('^i18n/$', set_language, name='set_language'),
    ]

urlpatterns += [
    url("^", include("vote.urls")),
    url('^', include('django.contrib.auth.urls')),
    url("^$", direct_to_template, {"template": "index.html"}, name="home"),
    url(r'^$', pages_view.page, {'slug': '/'}, name='home'),
    url(r'^', include('mezzanine.urls')),
]

handler404 = "mezzanine.core.views.page_not_found"
handler500 = "mezzanine.core.views.server_error"
