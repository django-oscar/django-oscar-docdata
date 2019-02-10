====================
django-oscar-docdata
====================

Payment gateway integration for `Docdata Payments <http://www.docdatapayments.com/>`_ in django-oscar_.
DocData Payments is a large payment gateway based in The Netherlands that supports more than
40 international payment methods.

.. _django-oscar: https://github.com/django-oscar/django-oscar

.. image:: https://travis-ci.org/django-oscar/django-oscar-docdata.svg?branch=master
    :target: https://travis-ci.org/django-oscar/django-oscar-docdata

.. image:: https://badge.fury.io/py/django-oscar-docdata.svg
   :alt: Latest PyPi release
   :target: https://pypi.python.org/pypi/django-oscar-docdata


Installation
============

Install via pip:

.. code-block:: bash

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

Add to ``urls.py``:

.. code-block:: python

    from oscar_docdata.dashboard.app import application as docdata_dashboard_app

    urlpatterns += [
        url(r'^api/docdata/', include('oscar_docdata.urls')),
        url(r'^dashboard/docdata/', include(docdata_dashboard_app.urls)),
    ]

Add to ``settings.py``:

.. code-block:: python

    OSCAR_DASHBOARD_NAVIGATION[2]['children'].insert(1, {
        'label': _('Docdata Orders'),
        'url_name': 'docdata-order-list',
    })

While developing, enabling logging for `suds` and `oscar_docdata` is recommended to see
detailed information:

.. code-block:: python

    LOGGING = {
        # ...
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
This module supports such use-case.

When you fill in the ``DOCDATA_MERCHANT_PASSWORDS`` dictionary,
orders submitted to any of these merchants can be displayed in the admin,
and they can receive status updates. Each key/value is a merchant-name/password pair.

When no subaccounts are configured, only the orders submitted by the current merchant can be displayed in the admin.
This supports a multi-tennant database structure, while each tennant only sees their own orders.


Integration into your project
-----------------------------

Please view the `sandbox application`_ how to integrate the application.
This includes the project-specific decisions such as:

* How to create payment events.
* How to create a custom facade class
* Which fields to map to the "house number" field. (e.g. ``line2``, ``line3`` or a custom field).
* Whether to cancel an order when the customer aborted the payment.
* When to submit confirmation emails.


Local development and running the tests
---------------------------------------

You can use the included Makefile to install a development environment and to run the flake8
checker and the testrunner. Make sure you do this inside a virtualenv:

.. code-block:: bash

    git clone git@github.com:django-oscar/django-oscar-docdata.git

    cd django-oscar-docdata
    make install
    make lint
    make test


Running the Sandbox application
-------------------------------

It is possible to run the `sandbox application`_ to test this package and to see if your
Docdata credentials work. You can set the `DOCDATA_MERCHANT_NAME` and the `DOCDATA_MERCHANT_PASSWORD`
environment variables before running `manage.py`:

.. code-block:: bash

    # creates a local sqlite database
    ./sandbox/manage.py migrate

    # loads some sample products (books)
    ./sandbox/manage.py oscar_import_catalogue sandbox/fixtures/books.csv

    # so you can fill out your shipping address
    ./sandbox/manage.py loaddata fixtures/countries.json

    # run the sandbox installation with the docdata merchant username and passord
    DOCDATA_MERCHANT_NAME=merchant DOCDATA_MERCHANT_PASSWORD=merchant ./sandbox/manage.py runserver

Docdata is really keen on having unique merchant order ids. Why is not really clear as they don't
use this references (they use their own). While testing it can happen that you run into an error
about unique merchant order ids. In that case you can set the following environment variable::

    # just a number which will be added to the submitted order id
    DOCDATA_ORDER_ID_START=99999

Configuration of the Docdata Backoffice
---------------------------------------

Make sure the following settings are configured:

* The "Payment Method names" need to be added to a profile (default value of ``DOCDATA_PROFILE`` is "standard").
* The notification URL and return URL need to be set. Example values:

 * Success: ``http://example.org/api/docdata/update_order/?callback=SUCCESS&order_id=``
 * Cancelled: ``http://example.org/api/docdata/update_order/?callback=CANCELLED&order_id=``
 * Error: ``http://example.org/api/docdata/update_order/?callback=ERROR&order_id=``
 * Pending: ``http://example.org/api/docdata/update_order/?callback=PENDING&order_id=``
 * Update URL: ``http://example.org/api/docdata/update_order/?order_id=``


Docdata Payment Service Specification
-------------------------------------

See the `paymentService <https://secure.docdatapayments.com/ps/orderapi-1_3.wsdl>`_ specification for
detailed technical information.

Caveats
=======

While working with the Docdata 1.0, 1.2 and 1.3 API, we found the following limitations:

* Address fields are oriented towards Dutch address standards.
  Passing international address fields is hard, or requires hacking, for example:

 * Faking the house number (because the US address fields have no official field for that).
 * Streets have a limit of 35 characters, so the "Address Line 1" should be truncated.

* Passing invalid address fields could cause PayPal, VISA or MasterCard transactions to fail.
* PayPal payments may fail when the "state" field is invalid (e.g. because of a typo). This is a check done by PayPal. Docdata however, passes that responsibility to the merchant (you).
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
* Be prepared to have XSD validation errors for bad input. For example, a bad postcode, house number or exceeding a max length leads to errors like::

    REQUEST_DATA_INCORRECT
    XML request does not match XSD. The data is: cvc-type.3.1.3: The value 'This is a wonderful product and campaign! Wish you a lot of luck!' of element 'ns0:description' is not valid

We hope this will be addressed by Docdata Payments in future versions of the API.


.. _`sandbox application`: https://github.com/django-oscar/django-oscar-docdata/tree/master/sandbox
