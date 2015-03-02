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

`DOCDATA_PROFILE`
    The payment-methods profile that is created in the Docdata Backoffice.
    By default, this is named "standard".

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

            'suds.transport': {
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

Extra: subaccount support
~~~~~~~~~~~~~~~~~~~~~~~~~

Docdata allows creating multiple accounts under the same contract.  This is called a "sub account".
Each account has it's own connections to VISA/MasterCard/PayPal/etc.
This module supports such situation.

When you fill in the ``DOCDATA_MERCHANT_PASSWORDS`` dictionary,
orders submitted to any of these merchants can be displayed in the admin,
and they can receive status updates. Each key/value is a merchant-name/password pair.

When no subaccounts are configured, only the orders submitted by the current merchant can be displayed in the admin.
This supports a multi-tennant database structure, while each tennant only sees their own orders.



Integration into your project
-----------------------------

Please view the `sandbox application`_ how to integrate the application.
This includes the project-specific desisions such as:

* How to create payment events.
* Which fields to map to the "house number" field. (e.g. ``line2``, ``line3`` or a custom field).
* Whether to cancel an order when the customer aborted the payment.
* When to submit confirmation emails.


Configuration of the Docdata Backoffice
---------------------------------------

Make sure the following settings are filled in:

* The "Payment Method names" need to be added to a profile (default value of ``DOCDATA_PROFILE`` is "standard").
* The notification URL and return URL need to be set. Example values:

 * Success: ``http://example.org/api/docdata/update_order/?callback=SUCCESS&order_id=``
 * Cancelled: ``http://example.org/api/docdata/update_order/?callback=CANCELLED&order_id=``
 * Error: ``http://example.org/api/docdata/update_order/?callback=ERROR&order_id=``
 * Pending: ``http://example.org/api/docdata/update_order/?callback=PENDING&order_id=``
 * Update URL: ``http://example.org/api/docdata/update_order/?order_id=``


Caveats
=======

While working with the Docdata 1.0 and 1.2 API, we found the following limitations:

* Address fields are oriented towards Dutch address standards.
  Passing international addressfields is hard, or requires hacking, for example:

 * Faking the house number (because the US address fields have no official field for that).
 * Streets have a limit of 35 characters, so the "Address Line 1" should be truncated.

* Passing invalid address fields could cause PayPal, VISA or MasterCard transactions to fail.
* PayPal payments may fail when the "state" field is invalid (e.g. because of a typoo). This is a check done by PayPal, Docdata passes the responsability to the merchant (you).
* The ``<billTo><address><state>`` field is typically ignored. Provide it via ``<invoice><shipTo><address><state>``. Seriously.
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


.. _`sandbox application`: https://github.com/edoburu/django-oscar-docdata/tree/master/sandbox
