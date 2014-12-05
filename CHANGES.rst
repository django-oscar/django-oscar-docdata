Changelog
=========

Version 1.2.4
-------------

* Added support for multiple merchant accounts in a single database (multi-tenant support).
* Added methods to ``DocdataOrder.objects``: ``current_merchant()``, ``for_reference()``, ``for_order()``.
* Added ``DOCDATA_FACADE_CLASS`` setting, so all views use a custom Facade
* Added ``oscar_docdata.gateway.to_iso639_part1()`` function, for sending language codes in the proper format.
* Added pagination in docdata dashboard view
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
