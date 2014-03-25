django-oscar-docdata
====================

Payment gateway integration for `Docdata Payments <http://www.docdatapayments.com/>`_ in django-oscar_.
DocData Payments is a large payment gateway based in The Netherlands that supports more then 40 international payment methods.

.. _django-oscar: https://github.com/tangentlabs/django-oscar


Installation
============

Install via pip::

    pip install django-oscar-docdata


Configuration
-------------

Configure the application:

`DOCDATA_MERCHANT_NAME`
    Credentials as supplied by the payment provider.

`DOCDATA_MERCHANT_PASSWORD`
    Credentials as supplied by the payment provider.

`DOCDATA_TESTING`
    Whether or not to run in testing mode. Defaults to `True`.

Add to ``urls.py``::

    from oscar_docdata.dashboard.app import application as docdata_app

    urlpatterns += patterns('',
        url(r'^api/docdata/', include('docdata.urls')),
        url(r'^dashboard/docdata/', include(docdata_app.urls)),
    )

Add to ``settings.py``::

    OSCAR_DASHBOARD_NAVIGATION[2]['children'].insert(1, {
        'label': _('Docdata Orders'),
        'url_name': 'docdata-order-list',
    })

As recommendation, temporary log all events from this package as well::

    LOGGING = {
        # ...

        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            # ...

            'suds': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'oscar_docdata': {
                'handlers': ['mail_admins', 'console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }
