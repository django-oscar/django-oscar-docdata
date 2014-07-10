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

Caveats
=======

While working with the Docdata 1.0 and 1.2 API, we found the following limitations:

* Address fields are oriented towards Dutch address standards.
  Passing international addressfields is hard, or requires hacking, for example:

 * faking the house number (because the US address fields have no official field for that).
 * Streets have a limit of 35 characters, so the "Address Line 1" should be truncated.

* Passing invalid address fields could cause PayPal, VISA or MasterCard transactions to fail.
* The individual payment objects have a status value, but the payment cluster does not.
  This means that there is no global status value to read.
  If an order has been cancelled before starting a payment, there is no way to tell from the API.
  The only way this can be detected, is when the customer presses the "Back to shop" link, which calls the cancel callback url.
  You may want to catch the ``return_view_called`` signal for this.
* Determining that an order has been paid happens by comparing "received >= expected".
  This could break with currency conversions.
  Again, because the payment cluster status is not exposed in the API.
  As workaround, there is a ``DOCDATA_PAYMENT_SUCCESS_MARGIN`` setting to add a margin of 100 cents.

We hope this will be addressed by Docdata Payments in future versions of the API.

