import os
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from oscar import get_core_apps, OSCAR_MAIN_TEMPLATE_DIR
from oscar.defaults import *  # noqa

PROJECT_DIR = os.path.dirname(__file__)
location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), x)  # noqa

DEBUG = True
USE_TZ = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': location('db.sqlite')
    }
}
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = location("public/media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# ADMIN_MEDIA_PREFIX = '/media/admin/'

STATIC_URL = '/static/'
STATICFILES_DIRS = (location('static/'),)
STATIC_ROOT = location('public')
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '$)a7n&o80u!6y5t-+jrd3)3!%vh&shg$wqpjpxc!ar&p#!)n1a'

# List of callables that know how to import templates from various sources.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            location('templates'),
            OSCAR_MAIN_TEMPLATE_DIR,
        ),
        'OPTIONS': {
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ),
            'context_processors': (
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Oscar specific
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.core.context_processors.metadata',
            ),
        },
    },
]

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
)

ROOT_URLCONF = 'sandbox.urls'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'oscar': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG is True else 'INFO',
        },
        'oscar_docdata': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG is True else 'INFO',
        },
    },
}


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'oscar_docdata',
    'widget_tweaks'
]

# our custom checkout app with docdata payment selection views
INSTALLED_APPS += get_core_apps(['sandbox.apps.checkout'])

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/accounts/'
APPEND_SLASH = True


# ==============
# Oscar settings
# ==============


OSCAR_ALLOW_ANON_CHECKOUT = False

OSCAR_DEFAULT_CURRENCY = "EUR"

# Haystack settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

OSCAR_SHOP_TAGLINE = 'Docdata Payments sandbox'

COMPRESS_ENABLED = False
COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
)

# =========================
# Docdata Payments settings
# =========================

# Test:
DOCDATA_MERCHANT_NAME = os.environ.get("DOCDATA_MERCHANT_NAME", "")
DOCDATA_MERCHANT_PASSWORD = os.environ.get("DOCDATA_MERCHANT_PASSWORD", "")
DOCDATA_TESTING = True

# URLs
DOCDATA_SUCCESS_URL = reverse_lazy('checkout:thank-you')
DOCDATA_PENDING_URL = reverse_lazy('checkout:thank-you')
DOCDATA_CANCELLED_URL = '/'
DOCDATA_ERROR_URL = '/'

# Extend dashboard
OSCAR_DASHBOARD_NAVIGATION[2]['children'].insert(1, {
    'label': _('Docdata Orders'),
    'url_name': 'docdata-order-list',
})

# Payment choices
WEBSHOP_PAYMENT_CHOICES = (
    ('IDEAL', 'iDEAL'),
    ('VISA', 'Visa'),
    ('MASTERCARD', 'MasterCard'),
    ('AMEX', 'American Express'),
    ('PAYPAL_EXPRESS_CHECKOUT', 'PayPal'),  # NOTE: has additional hack in checkout code for US.
)

# Order pipeline
OSCAR_INITIAL_ORDER_STATUS = 'new'  # The main object
OSCAR_INITIAL_LINE_STATUS = 'new'   # The individual lines
OSCAR_ORDER_STATUS_PIPELINE = {
    # Possible states of an order, and the transitions.
    'new': ('pending', 'paid', 'cancelled'),  # docdata started
    'pending': ('paid', 'cancelled'),
    'paid': ('shipping', 'delivered', 'charged back', 'refunded'),
    'refunded': (),       # Merchant refunded
    'charged back': (),   # Customer asked for charge back
    'cancelled': (),
    'expired': (),
    'shipping': ('delivered', 'refunded', 'charged back'),
    'delivered': ('refunded', 'charged back'),
}
OSCAR_ORDER_STATUS_PIPELINE['unknown'] = OSCAR_ORDER_STATUS_PIPELINE.keys()

OSCAR_LINE_STATUS_PIPELINE = OSCAR_ORDER_STATUS_PIPELINE

OSCAR_ORDER_STATUS_CASCADE = {
    # Let global states cascade to the order lines too.
    'paid': 'paid',
    'cancelled': 'cancelled',
    'charged back': 'charged back',
    'expired': 'expired',
}

DOCDATA_ORDER_STATUS_MAPPING = {
    # DocdataOrder status values: new, in_progress, pending, paid, charged_back, cancelled, refunded, unknown
    # Map to our order pipeline, just remove the underscores. All other values are identical.
    'in_progress': "pending",         # Redirect phase
    'charged_back': "charged back",
}

SHIPPING_EVENT_STATUS_MAPPING = {
    # Translate shipping event type to OSCAR_ORDER_STATUS_PIPELINE/OSCAR_LINE_STATUS_PIPELINE
    'shipping': 'shipping',
    'delivered': 'delivered',
}
