Changelog
=========

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
