"""
Bridging module between Oscar and the gateway module (which is Oscar agnostic)
"""
import logging
from django.utils.translation import get_language
from oscar.apps.payment.exceptions import PaymentError
from oscar_docdata import appsettings
from oscar_docdata.compat import get_model
from oscar_docdata.exceptions import DocdataCreateError
from oscar_docdata.gateway import Name, Shopper, Destination, Address, Amount, to_iso639_part1, Invoice, Vat, Item
from oscar_docdata.interface import Interface
from oscar_docdata.utils.load import import_class

__all__ = (
    'get_facade',
    'get_facade_class',
    'Facade',
)

logger = logging.getLogger(__name__)

Order = None
SourceType = None
_FacadeClass = None

def _lazy_get_models():
    # This avoids various import conflicts between apps that may
    # import the Facade before any other models.
    global Order
    global SourceType
    if Order is None:
        Order = get_model('order', 'Order')
        SourceType = get_model('payment', 'SourceType')


def get_facade(*args, **kwargs):
    """
    Get the proper Facade object instance.
    This reads the ``DOCDATA_FACADE_CLASS`` setting.
    """
    FacadeClass = get_facade_class()
    return FacadeClass(*args, **kwargs)


def get_facade_class():
    """
    Get the proper Facade object instance.
    This reads the ``DOCDATA_FACADE_CLASS`` setting.
    """
    global _FacadeClass
    if _FacadeClass is not None:
        return _FacadeClass

    # Import it.
    _FacadeClass = import_class(appsettings.DOCDATA_FACADE_CLASS, 'DOCDATA_FACADE_CLASS')
    return _FacadeClass



class Facade(Interface):
    """
    The bridge between Oscar and the generic Interface.

    Most methods are just called directly on the Interface.
    """

    def create_payment(self, order_number, total, user, language=None, description=None, profile=None, merchant_name=None, **kwargs):
        """
        Start a new payment session / container.

        :param order_number: The order number generated by Oscar.
        :param total: The price object, including totals and currency.
        :type total: :class:`oscar.core.prices.Price`
        :type user: :class:`django.contrib.auth.models.User`

        Besides the overwritten parameters, also provide:

        :param billing_address: The billing address, used
        :type billing_address: :class:`oscar.apps.address.abstract_models.AbstractAddress`
        :param basket: The basket to submit, to generate the invoice.
        :type basket: :class:`~oscar.apps.basket.abstract_models.AbstractBasket`
        :param shipping_address: The shipping address for the invoice.
        :type shipping_address: :class:`~oscar.apps.address.abstract_models.AbstractAddress`
        :returns: The Docdata order reference ("order key").

        ..note::
            The Docdata API v1.2 has issues with passing the address fields to PayPal.
            It read the "billing_address.state" field as "status", and as hack they
            now pass the "shipping_address.state" to PayPal.
            Hence, the recommended action is to pass the billing address as shipping address too.
        """
        if not profile:
            profile = appsettings.DOCDATA_PROFILE

        try:
            order_key = super(Facade, self).create_payment(order_number, total, user, language=language, description=description, profile=profile, merchant_name=merchant_name, **kwargs)
        except DocdataCreateError as e:
            raise PaymentError(e.value, e)

        return order_key



    def get_create_payment_args(self, order_number, total, user, language=None, description=None, profile=None, **kwargs):
        """
        The arguments for the createpayment call.
        This is a separate method to be easily overwritable.
        """
        if not profile:
            profile = appsettings.DOCDATA_PROFILE

        args = dict(
            order_id=order_number,
            total_gross_amount=Amount(total.incl_tax, total.currency),
            shopper=Shopper(
                id=user.id,
                name=Name(
                    first=user.first_name,
                    last=user.last_name,
                ),
                email=user.email,
                language=to_iso639_part1(language or get_language()),
                gender='U'
            ),
            description=description,
            profile=profile
        )

        # Pass extra fields, needed to handle certain payment types property.
        # That includes PayPal.

        _billingaddress = kwargs.get('billingaddress', None)  # Old name
        billing_address = kwargs.get('billing_address', _billingaddress)
        if billing_address is not None:
            bill_to = Destination.from_address(billing_address)
            # Auto fill in these fields if they are not provided.
            # These fields are not required in Oscar, but Docdata requires them.
            if not bill_to.name.first:
                bill_to.name.first = user.first_name
            if not bill_to.name.last:
                bill_to.name.last = user.last_name

            args['bill_to'] = bill_to

        shipping_address = kwargs.get('shipping_address', None)
        basket = kwargs.get('basket', None)
        if shipping_address is not None and basket is not None:
            invoice = Invoice.from_basket(basket, total, shipping_address)
            # Auto fill in these fields if they are not provided.
            # These fields are not required in Oscar, but Docdata requires them.
            if not invoice.ship_to.name.first:
                invoice.ship_to.name.first = user.first_name
            if not invoice.ship_to.name.last:
                invoice.ship_to.name.last = user.last_name

            args['invoice'] = invoice

        return args


    def order_status_changed(self, docdataorder, old_status, new_status):
        """
        The order status changed.
        """
        _lazy_get_models()
        project_status = appsettings.DOCDATA_ORDER_STATUS_MAPPING.get(new_status, new_status)
        cascade = appsettings.OSCAR_ORDER_STATUS_CASCADE.get(project_status, None)

        # Update the order in Oscar
        # Using select_for_update() to have a lock on the order first.
        order = Order.objects.select_for_update().get(number=docdataorder.merchant_order_id)
        if order.status == project_status:
            # Parallel update by docdata (return URL and callback), avoid sending the signal twice to the user code.
            logging.info("Order {0} status is already {1}, skipping signal.".format(order.number, order.status))
            return

        # Not using Order.set_status(), forcefully set it to the current situation.
        order.status = project_status
        if cascade:
            order.lines.all().update(status=cascade)
        order.save()

        # Send the signal
        super(Facade, self).order_status_changed(docdataorder, old_status, new_status)


    def get_source_type(self):
        """
        Convenience method, return the canonical SourceType for Docdata payment events.
        """
        _lazy_get_models()
        source_type, _ = SourceType.objects.get_or_create(code='docdata', defaults={'name': "Docdata Payments"})
        return source_type
