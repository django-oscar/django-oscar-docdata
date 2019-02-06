from django.conf import settings
from django.contrib.auth import get_user_model

from datetime import timedelta

from oscar.core.loading import get_class, get_model

from oscar_docdata.models import DocdataOrder


import pytest

User = get_user_model()

Basket = get_model('basket', 'Basket')
Product = get_model('catalogue', 'Product')
ShippingAddress = get_model('order', 'ShippingAddress')
UserAddress = get_model('address', 'UserAddress')
Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')
OrderCreator = get_class('order.utils', 'OrderCreator')
OrderNumberGenerator = get_class('order.utils', 'OrderNumberGenerator')
OrderTotalCalculator = get_class(
    'checkout.calculators', 'OrderTotalCalculator')
Repository = get_class('shipping.repository', 'Repository')
Selector = get_class('partner.strategy', 'Selector')


@pytest.fixture()
def customer():
    return User.objects.get(username="customer")


@pytest.fixture()
def django_app(django_app, customer):
    django_app.set_user(customer.username)
    return django_app


@pytest.fixture()
def book():
    return Product.objects.get(title="Expert C Programming")


@pytest.fixture()
def basket(customer, book):
    basket = Basket.objects.create(owner=customer)
    basket.strategy = Selector().strategy(request=None, user=customer)
    basket.add_product(book)
    return basket


@pytest.fixture()
def shipping_address(customer):
    user_address = UserAddress.objects.get(user=customer)
    shipping_address = ShippingAddress()
    user_address.populate_alternative_model(shipping_address)
    shipping_address.save()
    return shipping_address


@pytest.fixture()
def source_type():
    return SourceType.objects.get(code="docdata")


@pytest.fixture()
def oscar_order(basket, shipping_address):
    order_number = OrderNumberGenerator().order_number(basket)
    shipping_method = Repository().get_default_shipping_method(
        basket=basket,
        user=basket.owner,
        request=None,
        shipping_addr=shipping_address)
    shipping_charge = shipping_method.calculate(basket)

    return OrderCreator().place_order(
        basket=basket,
        total=OrderTotalCalculator().calculate(
            basket, shipping_charge),
        shipping_method=shipping_method,
        shipping_charge=shipping_charge,
        user=basket.owner,
        shipping_address=shipping_address,
        order_number=order_number
    )


@pytest.fixture()
def docdata_order(oscar_order, book, source_type):
    docdata_order = DocdataOrder.objects.create(
        merchant_name=settings.DOCDATA_MERCHANT_NAME,
        merchant_order_id=oscar_order.number,
        order_key="DE6A6E24F046FB24094E9208C66FEFE7",
        status=DocdataOrder.STATUS_NEW,
        total_gross_amount=oscar_order.total_incl_tax
    )
    Source.objects.create(
        order=oscar_order,
        source_type=source_type,
        amount_allocated=oscar_order.total_incl_tax,
        reference=docdata_order.order_key
    )
    return docdata_order


@pytest.fixture()
def expired_docdata_order(docdata_order):
    # first set the created date on longer than three weeks ago
    docdata_order.created = docdata_order.created - timedelta(days=22)
    docdata_order.order_key = "expired-order-key"
    docdata_order.save()
    return docdata_order
