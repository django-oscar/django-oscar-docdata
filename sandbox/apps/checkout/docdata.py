import datetime
import logging

from django.contrib import messages
from django.dispatch import receiver
from django.http import HttpRequest
from django.utils import translation

from oscar.apps.payment.abstract_models import AbstractTransaction
from oscar.core.loading import get_class, get_model

from oscar_docdata import signals
from oscar_docdata.exceptions import DocdataStatusError
from oscar_docdata.facade import Facade
from oscar_docdata.models import DocdataOrder

logger = logging.getLogger(__name__)

Source = get_model('payment', 'Source')
Order = get_model('order', 'Order')
PaymentEventType = get_model('order', 'PaymentEventType')
PaymentEvent = get_model('order', 'PaymentEvent')
PaymentEventQuantity = get_model('order', 'PaymentEventQuantity')
EventHandler = get_class('order.processing', 'EventHandler')
OrderPlacementMixin = get_class('checkout.mixins', 'OrderPlacementMixin')


class CustomDocdataFacade(Facade):
    """
    Improve the Docdata facade, to pass our way of storing address info,
    """
    def get_create_payment_args(self, *args, **kwargs):
        api_args = super(CustomDocdataFacade, self).get_create_payment_args(*args, **kwargs)

        # Make sure the address can be accepted by Docdata.
        # Streets have a limit of 32 characters (already truncated)
        if not api_args['bill_to'].address.house_number:
            # This seriously needs to be a number for PayPal to work in Docdata!
            api_args['bill_to'].address.house_number = "1"

        # HACK! Pass customer "State" field for PayPal.
        # Hack the invoice so we can provide another STATE field to make PayPal work.
        # Though this should be the shipping address,
        # using the billing address here because Docdata reads that field.
        # Seriously. This is messed up.
        api_args['invoice'].ship_to = api_args['bill_to']

        # Docdata expects unique merchant order numbers, but they don't do
        # anything with it so you can send here any number you like. The
        # callback from docdata is working with docdata references, not
        # with merchant order id's
        # We insert a date here so that the number is always unique:
        now = datetime.datetime.utcnow()
        api_args['order_id'] = "%s-%s" % (now.strftime("%Y%m%d-%H%M%S"), api_args['order_id'])

        return api_args


@receiver(signals.payment_added)
def _on_payment_added(order, payment, **kwargs):
    """
    :type order: :class:`oscar_docdata.models.DocdataOrder`
    :type payment: :class:`oscar_docdata.models.DocdataPayment`
    """
    source = Source.objects.get(order__number=order.merchant_order_id)

    source.amount_debited = order.total_captured
    source.amount_refunded = order.total_refunded
    source.save()

    # Create a Oscar transaction for our payment source.
    if not source.transactions.filter(reference=payment.payment_id).exists():
        if payment.amount_allocated:
            source.transactions.create(
                txn_type=AbstractTransaction.AUTHORISE, amount=payment.amount_allocated,
                reference=payment.payment_id, status=payment.status
            )
        elif payment.amount_debited:
            source.transactions.create(
                txn_type=AbstractTransaction.DEBIT, amount=payment.amount_debited,
                reference=payment.payment_id, status=payment.status
            )
        elif payment.amount_refunded:
            source.transactions.create(
                txn_type=AbstractTransaction.REFUND, amount=payment.amount_refunded,
                reference=payment.payment_id, status=payment.status
            )
        elif payment.amount_chargeback:
            source.transactions.create(
                txn_type='Changeback', amount=payment.amount_chargeback,
                reference=payment.payment_id, status=payment.status
            )
        else:
            source.transactions.create(
                txn_type='Unknown', amount=payment.amount_allocated or payment.amount_chargeback or payment.amount_debited or payment.amount_refunded,
                reference=payment.payment_id, status=payment.status
            )


@receiver(signals.payment_updated)
def _on_payment_updated(order, payment, **kwargs):
    """
    :type order: :class:`oscar_docdata.models.DocdataOrder`
    :type payment: :class:`oscar_docdata.models.DocdataPayment`
    """
    source = Source.objects.get(order__number=order.merchant_order_id)
    source.amount_debited = order.total_captured
    source.amount_refunded = order.total_refunded
    source.save()

    # TODO: Not updating the transaction yet...


@receiver(signals.order_status_changed)
def _on_order_status_updated(order, **kwargs):
    """
    :type order: :class:`oscar_docdata.models.DocdataOrder`
    """
    # As extra safe guard, so update totals when status updates.
    source = Source.objects.get(order__number=order.merchant_order_id)
    source.amount_debited = order.total_captured
    source.amount_refunded = order.total_refunded
    source.save()

    # Show relevant docdata events in Oscar Dashboard too.
    oscar_order = Order.objects.get(number=order.merchant_order_id)

    if order.status == DocdataOrder.STATUS_PAID:
        add_payment_event(oscar_order, "paid", order.total_captured, reference=order.order_key)

        # Notify the eventhandler that the status was changed.
        ev = EventHandler(user=oscar_order.user)
        ev.handle_order_status_change(oscar_order, "paid")

        # Send confirmation email
        request = HttpRequest()
        send_confirmation_message(request, order)

    elif order.status == DocdataOrder.STATUS_CHARGED_BACK:
        add_payment_event(oscar_order, "charged-back", order.total_charged_back, reference=order.order_key)
    elif order.status == DocdataOrder.STATUS_REFUNDED:
        add_payment_event(oscar_order, "refunded", order.total_refunded, reference=order.order_key)
    elif order.status == DocdataOrder.STATUS_CANCELLED:
        add_payment_event(oscar_order, "cancelled", order.total_registered, reference=order.order_key)
    else:
        raise DocdataStatusError(0, "Unknown order status: %s" % order.status)


@receiver(signals.return_view_called)
def _on_return_view_called(request, order, callback, **kwargs):
    """
    :type order: :class:`oscar_docdata.models.DocdataOrder`
    """
    if callback in ('CANCELLED', 'ERROR'):
        # If the payment menu was cancelled before a payment method selected,
        # docdata registers that there is no payment at all.
        # Cluster state = started, but there is no payment object at all.
        msg = "Received {0} state at return view, cancelling order {1}".format(callback, order.merchant_order_id)
        logger.info(msg)
        messages.error(request, msg)
        order.cancel()

        # restore the frozen basket into the active basket so we can checkout again
        oscar_order = Order.objects.get(number=order.merchant_order_id)
        request.basket.merge(oscar_order.basket)
    else:
        msg = "Received {0} state at return view for order {1}".format(callback, order.merchant_order_id)
        logger.info(msg)
        messages.success(request, msg)


class SendConfirmationEmail(OrderPlacementMixin):
    """
    Sending the confirmation email is deferred after payment. Using
    the OrderPlacementMixin class makes sure we use oscars
    send_confirmation_message
    """
    def __init__(self, request):
        self.request = request


def send_confirmation_message(request, docdata_order):
    # Don't continue as anonymous Docdata API user, but the user related to the order.
    # The send_confirmation_message() also expects request.user to be there.
    oscar_order = Order.objects.get(number=docdata_order.merchant_order_id)
    request.user = oscar_order.user
    logger.info("Sending order confirmation for {0}".format(oscar_order.number))

    with translation.override(docdata_order.language):
        SendConfirmationEmail(request).send_confirmation_message(
            oscar_order, 'ORDER_PLACED')


def add_payment_event(order, event_type_name, amount, reference=''):
    """
    Record a payment event for creation once the order is placed
    """
    event_type, __ = PaymentEventType.objects.get_or_create(name=event_type_name)
    event = PaymentEvent.objects.create(event_type=event_type, order=order, amount=amount, reference=reference)

    # We assume all lines are involved in the payment event
    for line in order.lines.all():
        PaymentEventQuantity.objects.create(event=event, line=line, quantity=line.quantity)

    return event
