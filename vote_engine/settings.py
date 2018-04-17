
from __future__ import absolute_import, unicode_literals
import os

from django import VERSION as DJANGO_VERSION
from django.utils.translation import ugettext_lazy as _


SITE_TITLE = "Конкурсы"
ADMIN_SITE_TITLE = "Конкурсы"

ADMIN_MENU_ORDER = (
    ("Content", ("pages.Page", "blog.BlogPost", "generic.ThreadedComment", (_("Media Library"), "media-library"),)),
    ("Site", ("sites.Site", "redirects.Redirect", "conf.Setting")),
    ("Users", ("auth.User", "auth.Group",)),
)

LOGIN_URL = '/login/'

ADMIN_REMOVAL = (
    'mezzanine.generic.models.ThreadedComment',
)

USE_MODELTRANSLATION = False

ALLOWED_HOSTS = ['*']

TIME_ZONE = 'Asia/Vladivostok'

USE_TZ = True

LANGUAGE_CODE = "en"

LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
)

DEBUG = False

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SITE_ID = 1

USE_I18N = True
USE_L10N = True

AUTHENTICATION_BACKENDS = ("mezzanine.core.auth_backends.MezzanineBackend",)

FILE_UPLOAD_PERMISSIONS = 0o644

DATABASES = {
    "default": {
        # Add "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.",
        # DB name or path to database file if using sqlite3.
        "NAME": "",
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}


PROJECT_APP_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_APP = os.path.basename(PROJECT_APP_PATH)
PROJECT_ROOT = BASE_DIR = os.path.dirname(PROJECT_APP_PATH)

CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_APP

STATIC_URL = "/static/"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList']
        ],
        'width': '100%',
    }
}

CKEDITOR_BASEPATH = STATIC_URL + "ckeditor/ckeditor"

STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL.strip("/"))

MEDIA_URL = STATIC_URL + "media/"

MEDIA_ROOT = os.path.join(PROJECT_ROOT, *MEDIA_URL.strip("/").split("/"))

ROOT_URLCONF = "%s.urls" % PROJECT_APP

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_ROOT, "templates"),
            os.path.join(PROJECT_ROOT, "vote", "templates"),
            os.path.join(PROJECT_ROOT, "vote", "templates", "vote"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.static",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.tz",
                "mezzanine.conf.context_processors.settings",
                "mezzanine.pages.context_processors.page"
            ],
            "builtins": [
                "mezzanine.template.loader_tags",
            ],
        },
    },
]

if DJANGO_VERSION < (1, 9):
    del TEMPLATES[0]["OPTIONS"]["builtins"]


INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.redirects",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "hitcount",
    "mezzanine.boot",
    "mezzanine.conf",
    "mezzanine.core",
    "mezzanine.generic",
    "mezzanine.pages",
    "mezzanine.blog",
    "mezzanine.forms",
    "mezzanine.galleries",
    "vote",
    "ckeditor",
    "bootstrap3",
)

MIDDLEWARE_CLASSES = (
    "mezzanine.core.middleware.UpdateCacheMiddleware",

    'django.contrib.sessions.middleware.SessionMiddleware',
    # Uncomment if using internationalisation or localisation
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "mezzanine.core.request.CurrentRequestMiddleware",
    "mezzanine.core.middleware.RedirectFallbackMiddleware",
    "mezzanine.core.middleware.TemplateForDeviceMiddleware",
    "mezzanine.core.middleware.TemplateForHostMiddleware",
    "mezzanine.core.middleware.AdminLoginInterfaceSelectorMiddleware",
    "mezzanine.core.middleware.SitePermissionMiddleware",
    "mezzanine.pages.middleware.PageMiddleware",
    "mezzanine.core.middleware.FetchFromCacheMiddleware",
)

PACKAGE_NAME_FILEBROWSER = "filebrowser_safe"
PACKAGE_NAME_GRAPPELLI = "grappelli_safe"

OPTIONAL_APPS = (
    "debug_toolbar",
    "django_extensions",
    "compressor",
    PACKAGE_NAME_FILEBROWSER,
    PACKAGE_NAME_GRAPPELLI,
)

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
PROFILE = '/accounts/profile/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = ''
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = ''

f = os.path.join(PROJECT_APP_PATH, "local_settings.py")
if os.path.exists(f):
    import sys
    import imp
    module_name = "%s.local_settings" % PROJECT_APP
    module = imp.new_module(module_name)
    module.__file__ = f
    sys.modules[module_name] = module
    exec(open(f, "rb").read())

try:
    from mezzanine.utils.conf import set_dynamic_settings
except ImportError:
    pass
else:
    set_dynamic_settings(globals())
