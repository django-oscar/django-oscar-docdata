import pytest

from oscar_docdata.models import DocdataOrder

from tests.testdata import docdata_responses


@pytest.mark.django_db
def test_checkout_payment_success(
        django_app, customer, user_address, basket, mailoutbox, mock_transport):
    """
    Just do a simple checkout to see if basic stuff is working

    We already have a customer, a shipping address and a filled basket
    """
    # first make sure we return a create payment response and after that a
    # status response
    mock_transport.set_responses([
        docdata_responses.CREATE_PAYMENT_RESPONSE,
        docdata_responses.STATUS_SUCCESS_RESPONSE
    ])

    # go to the checkout page
    response = django_app.get("/checkout/").maybe_follow()

    # select the predefined shipping address
    form = response.forms['select_shipping_address_1']
    response = form.submit().maybe_follow()

    # here we are at the payment menu, let's select IDEAL:
    form = response.form
    form['payment_method'] = 'IDEAL'
    response = form.submit().maybe_follow()

    # go to the confirmation page:
    response = response.click(linkid='view_preview').maybe_follow()

    # now it is time to 'redirect to docdata'. The call to create a payment is made and
    # the redirect url should be in our response
    form = response.form
    response = form.submit()

    assert response.status == "302 Found"
    assert response.location.startswith(
        "https://test.docdatapayments.com/ps/")

    # now we pretend the success callback:
    django_app.get(
        "/api/docdata/return/?callback=SUCCESS&order_id=DE6A6E24F046FB24094E9208C66FEFE7")

    # so a confirmation email has been sent
    assert len(mailoutbox) == 1


@pytest.mark.django_db
def test_payment_cancelled(django_app, cancelled_docdata_order, mock_transport):
    """
    It's also possible to cancel a payment once arrived at the docdata payment menu
    """
    # now return the status response: three times docdata will be queried
    mock_transport.set_responses([
        docdata_responses.STATUS_CANCELLED_RESPONSE,
        docdata_responses.CANCELLED_PAYMENT_RESPONSE,
        docdata_responses.STATUS_CANCELLED_RESPONSE,
    ])

    order_key = cancelled_docdata_order.order_key

    # now we pretend the cancelled callback
    response = django_app.get(
        "/api/docdata/return/?callback=CANCELLED&order_id={}".format(order_key)).maybe_follow()
    assert response.status == "200 OK"

    cancelled_docdata_order.refresh_from_db()

    assert cancelled_docdata_order.status == DocdataOrder.STATUS_CANCELLED
