from datetime import timedelta

from django.core.management import call_command

from six import StringIO

import pytest


@pytest.mark.django_db
def test_manage_update_docdata_order_all(docdata_order, oscar_order):
    # this will query docdata to see if the orders are paid
    call_command("update_docdata_order", "--all")

    docdata_order.refresh_from_db()
    oscar_order.refresh_from_db()

    # the mocked suds client will confirm that they are paid
    assert docdata_order.status == docdata_order.STATUS_PAID
    assert oscar_order.status == 'paid'


@pytest.mark.django_db
def test_manage_update_docdata_order_single(docdata_order, oscar_order):
    # this will query docdata to see if the orders are paid
    call_command("update_docdata_order", oscar_order.number)

    docdata_order.refresh_from_db()
    oscar_order.refresh_from_db()

    assert docdata_order.status == docdata_order.STATUS_PAID
    assert oscar_order.status == 'paid'


@pytest.mark.django_db
def test_manage_expire_docdata_orders_status_expired(expired_docdata_order):
    # mark docdata orders as expired when docdata says so
    call_command("expire_docdata_orders")

    expired_docdata_order.refresh_from_db()
    assert expired_docdata_order.status == expired_docdata_order.STATUS_EXPIRED


@pytest.mark.django_db
def test_manage_expire_docdata_orders_status_paid(docdata_order):
    # expired orders (created longer than 21 days ago) which are missed in the whole
    # process will still be marked as paid
    docdata_order.created = docdata_order.created - timedelta(days=22)
    docdata_order.save()

    call_command("expire_docdata_orders")

    docdata_order.refresh_from_db()
    assert docdata_order.status == docdata_order.STATUS_PAID


@pytest.mark.django_db
def test_manage_docdata_report(docdata_order):
    output = StringIO()
    call_command("docdata_report", "--status", "new", stdout=output)

    # just test that the report is printing something
    assert len(output.getvalue()) > 0
