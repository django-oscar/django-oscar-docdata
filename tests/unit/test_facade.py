import pytest

from oscar_docdata.exceptions import DocdataStatusError
from oscar_docdata.facade import Facade
from tests.suds_transport import ORDER_KEY


@pytest.mark.django_db
def test_facade_create_payment(oscar_order, mock_total_from_oscar_order):
    facade = Facade(testing_mode=True)

    docdata_order_key = facade.create_payment(
        order_number=oscar_order.number,
        total=mock_total_from_oscar_order(oscar_order),
        user=oscar_order.user,
        billing_address=oscar_order.billing_address
    )
    # ORDER_KEY is the hardocded expected results
    assert docdata_order_key == ORDER_KEY


@pytest.mark.django_db
def test_facade_order_status_changed(docdata_order):
    facade = Facade(testing_mode=True)
    # the report was stored first with a status change so the docdata order status is
    # already changed
    docdata_order.status = "paid"
    facade.order_status_changed(docdata_order, "new", "paid")


@pytest.mark.django_db
def test_facade_order_status_changed_wrong_status(docdata_order):
    facade = Facade(testing_mode=True)

    # the docdata order has still status 'new' so this should raise an exception
    with pytest.raises(DocdataStatusError) as e:
        facade.order_status_changed(docdata_order, "new", "paid")
    assert e.value.value == 'Unknown order status: new'


@pytest.mark.django_db
def test_facade_source_type():
    facade = Facade(testing_mode=True)
    source_type = facade.get_source_type()

    assert source_type.code == "docdata"
    assert source_type.name == "Docdata Payments"
