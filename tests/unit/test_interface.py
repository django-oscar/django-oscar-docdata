import pytest

from oscar_docdata.interface import Interface


@pytest.mark.django_db
def test_initialize():
    # this will query docdata to see if the orders are paid
    interface = Interface(testing_mode=True)
    assert interface.testing_mode is True
    # 'merchant' is set in the environment
    assert interface.client.merchant._name == 'merchant'


@pytest.mark.django_db
def test_interface_for_merchant():
    # we can also create an interface for a specific merchants
    interface = Interface.for_merchant(merchant_name='merchant', testing_mode=True)
    assert interface.testing_mode is True
    assert interface.client.merchant._name == 'merchant'


@pytest.mark.django_db
def test_create_payment(docdata_order, oscar_order, mock_total_from_oscar_order):
    interface = Interface(testing_mode=True)

    # this should raise an NotImplementedError as it should be implemented by a Facade
    with pytest.raises(NotImplementedError):
        interface.create_payment(
            order_number=oscar_order.number,
            total=mock_total_from_oscar_order(oscar_order),
            user=oscar_order.user
        )
