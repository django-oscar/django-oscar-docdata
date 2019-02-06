Changelog
=========

Version structure: the "1.2" refers to the Docdata API version.


Version 1.2.12 (2019-02-06)
---------------------------

* Added Python 3 and Django classifiers and wheel package
* Dropped Django < 1.11 and added support for Django 1.11, 2.0 and 2.1
* Fixed management commands to work with Django>=1.11
* Cleanup and simplified sandbox application
* Removed unused `django-polymorphic` dependency and cleanup up depending model

Version 1.2.11 (2018-03-07)
---------------------------

* Added Python 3 support.

Version 1.2.10
--------------

* Fixed Django 1.9+ support in templates.

Version 1.2.9
-------------

* Fixed the ``default`` value of the ``merchant_name`` field in the migrations.

Version 1.2.8
-------------

* Fixed Django 1.10 deprecation warnings

Version 1.2.7
-------------

* Added django-polymorphic 0.8 support

Version 1.2.6
-------------

* Added Django 1.7 migrations

Version 1.2.5
-------------

* Cache Docdata WSDL information, avoid fetching it each time ``Facade``/``Interface``/``DocdataClient`` object is constructed.
* Added ``DocdataClient.set_merchant(name, password)`` method.
* Added subaccount support

 * Added ``merchant_name`` parameter to ``create_payment()``.
 * Fill ``DOCDATA_MERCHANT_PASSWORDS`` to support updating/cancelling orders created at other subaccounts.
 * Minor **backwards incompatibility**: ``start_payment()`` "order_key" parameter is renamed to "order".
   This only affects passing kwargs. Passing the order key works but is deprecated, pass a ``DocdataOrder`` instead.

* Added ``update_docdata_order`` management command.
* Added ``-v3`` flag for managements commands to displays the SOAP XML conversation (via logging).
* Allow ``return_view_called`` signal handlers to return a response, thereby overriding the default response.
* Increased ``DOCDATA_PAYMENT_SUCCESS_MARGIN`` for USD to $1.50
* Fix reverting order statuses, using ``Order.set_status()`` now so manually changed order statuses are not reversed.
* Fix detecting "paid" status when the customer starts multiple payment attempts, but then completes the first.
  (the root issue here is the lack of a missing global "cluster/order status" field in the API - so we have to make guesses).
* Fix handling of paid orders that have a partial refund (e.g. 5%).
* Fix handling of orders with received a chargeback.
* Fix using ``%s`` in logging statements so Sentry can group similar events.
* Fix ``DocdataOrder.last_payment`` property.

Version 1.2.4
-------------

* Added support for multiple merchant accounts in a single database (multi-tenant support).
* Added manager methods to ``DocdataOrder.objects``: ``current_merchant()``, ``for_reference()``, ``for_order()``.
* Added support for the parameters ``billing_address``, ``shipping_address``, ``basket`` in the `get_create_payment_args()` code.
* Added support for the ``Invoice`` element. This is needed to pass state for PayPal.
* Added ``DOCDATA_FACADE_CLASS`` setting, so all views use a custom Facade
* Added ``DOCDATA_HOUSE_NUMBER_FIELD`` setting.
* Added ``oscar_docdata.gateway.to_iso639_part1()`` function, for sending language codes in the proper format.
* Added pagination in docdata dashboard view.
* Using suds-jurko_ fork for SOAP calls, which is a maintained fork of suds_.
* Fix detecting expired orders via the status API.
* Improve ``/api/docdata/update/`` output for curl usage.

Version 1.2.3
-------------

* Fix concurrency issues with Docdata calling both the return_url and notification_url at the same time.
* Apply 32 char limit to street field in the default `get_create_payment_args()` implementation.

Version 1.2.2
-------------

* Add management command ``expire_docdata_orders``
* Add management command ``docdata_report``
* Be more strict with payment tags, check for ``capture=CAPTURED``
* Explicitly set ``DocdataException.value`` to be a unicode string.
* Fix possible circular import errors when using ``Facade`` in ``models.py``
* Avoid warning for undocumented ``AUTHORIZATION_ERROR`` and ``CANCEL_FAILED`` status value.

Version 1.2.1
-------------

* Add ``DOCDATA_PAYMENT_SUCCESS_MARGIN`` setting to handle currency conversion rate issues.
* Avoid warning for undocumented ``AUTHORIZATION_FAILED`` status value.
* Mention 32 character limit for street fields in the README and sandbox.

Version 1.2
-----------

* Upgraded to Docdata 1.2 API

Version 1.0
-----------

* Released stable version after months of internal usage.


.. _suds: https://fedorahosted.org/suds/
.. _suds-jurko: https://bitbucket.org/jurko/suds
