import pytest


@pytest.mark.django_db
def test_checkout(django_app, customer, basket, mailoutbox):
    """
    Just do a simple checkout to see if basic stuff is working

    We already have a customer, a shipping address and a filled basket
    """
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
    response = django_app.get(
        "/api/docdata/return/?callback=SUCCESS&order_id=DE6A6E24F046FB24094E9208C66FEFE7")

    # so a confirmation email has been sent
    assert len(mailoutbox) == 1
