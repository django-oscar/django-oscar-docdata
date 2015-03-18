import logging
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db.models import get_model
from oscar.core.loading import get_class

logger = logging.getLogger(__name__)

Dispatcher = get_class('customer.utils', 'Dispatcher')
CommunicationEventType = get_model('customer', 'CommunicationEventType')
CommunicationEvent = get_model('order', 'CommunicationEvent')



def send_confirmation_message_once(request, order, communication_type_code='ORDER_PLACED', **kwargs):
    #if not EmailTracker.track(order, communication_type_code, request.user):
    if True:
        logger.info("Sending order confirmation for {0}".format(order.number))
        send_confirmation_message(request, order, communication_type_code, **kwargs)
    else:
        logger.info("Skipping order confirmation for {0}, is already sent".format(order.number))



#
# Based on OrderPlacementMixin.send_confirmation_message().
# The order confirmation needed to be sent later then the actual saving of the order.
#

def send_confirmation_message(request, order, communication_type_code='ORDER_PLACED', **kwargs):
    code = communication_type_code
    messages, event_type = get_email_message(request, order, communication_type_code)

    if messages and messages['body']:
        logger.info("Order #%s - sending %s messages", order.number, code)
        dispatcher = Dispatcher(logger)
        dispatcher.dispatch_order_messages(order, messages,
                                           event_type, **kwargs)
    else:
        logger.warning("Order #%s - no %s communication event type",
                       order.number, code)


def get_email_message(request, order, communication_type_code='ORDER_PLACED'):
    code = communication_type_code
    user = order.user if order.user_id else request.user
    ctx = {'user': user,
           'order': order,
           'site': order.site,
           'lines': order.lines.all()}

    if not user.is_authenticated():
        # Attempt to add the anon order status URL to the email template
        # ctx.
        try:
            path = reverse('customer:anon-order',
                           kwargs={'order_number': order.number,
                                   'hash': order.verification_hash()})
        except NoReverseMatch:
            # We don't care that much if we can't resolve the URL
            pass
        else:
            site = get_current_site(request)
            ctx['status_url'] = 'http://%s%s' % (site.domain, path)

    try:
        event_type = CommunicationEventType.objects.get(code=code)
    except CommunicationEventType.DoesNotExist:
        # No event-type in database, attempt to find templates for this
        # type and render them immediately to get the messages.  Since we
        # have not CommunicationEventType to link to, we can't create a
        # CommunicationEvent instance.
        messages = CommunicationEventType.objects.get_and_render(code, ctx)
        event_type = None
    else:
        # Create CommunicationEvent
        CommunicationEvent._default_manager.create(
            order=order, event_type=event_type)
        messages = event_type.get_messages(ctx)

    return messages, event_type
