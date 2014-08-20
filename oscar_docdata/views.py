import logging
from django.http import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse, HttpResponseNotFound, Http404, \
    HttpResponseServerError
from django.utils import translation
from django.views.generic import View
from oscar.core.loading import get_class
from oscar_docdata import appsettings
from oscar_docdata.compat import transaction_atomic
from oscar_docdata.exceptions import DocdataStatusError
from oscar_docdata.facade import Facade
from oscar_docdata.models import DocdataOrder
from oscar_docdata.signals import return_view_called, status_changed_view_called

logger = logging.getLogger(__name__)

OrderPlacementMixin = get_class('checkout.mixins', 'OrderPlacementMixin')


class UpdateOrderMixin(object):
    """
    Base mixin for updating the order from the API or return URL.
    """

    # What docdata calls the order_id, we call the order_key
    # Docdata uses both the order_key and merchant_order_id in the requests, depending on the view.
    order_query_arg = 'order_id'
    order_slug_field = 'order_key'
    facade_class = Facade

    def get_order_slug(self):
        try:
            return self.request.GET[self.order_query_arg]
        except KeyError:
            raise KeyError("Missing {0} parameter".format(self.order_query_arg))

    def get_order(self, order_slug):
        """
        Update the status of an order, by fetching the latest state from docdata.
        """
        # Try to find the order.
        # Block any other requests on the order until the status change is handled.
        try:
            return DocdataOrder.objects.select_for_update().get(**{self.order_slug_field: order_slug})
        except DocdataOrder.DoesNotExist:
            logger.error("Order {0}='{1}' not found to update payment status.".format(self.order_slug_field, order_slug))
            raise Http404(u"Order {0}='{1}' not found!".format(self.order_slug_field, order_slug))

    def update_order(self, order):
        # Ask the facade to request the status, and update the order accordingly.
        facade = self.facade_class()
        facade.update_order(order)


class OrderReturnView(UpdateOrderMixin, OrderPlacementMixin, View):
    """
    The view to redirect to after a successful order creation.
    """
    order_slug_field = 'order_key'
    success_url = appsettings.DOCDATA_SUCCESS_URL
    pending_url = appsettings.DOCDATA_PENDING_URL
    cancelled_url = appsettings.DOCDATA_CANCELLED_URL
    error_url = appsettings.DOCDATA_ERROR_URL

    def get(self, request, *args, **kwargs):
        # Directly query the latest state from Docdata
        try:
            order_key = self.get_order_slug()
        except KeyError as e:
            return HttpResponseBadRequest(e.message, content_type='text/plain; charset=utf-8')

        callback = request.GET.get('callback') or ''
        logger.info("Returned from Docdata for {0}, callback: {1}".format(order_key, callback))

        # Need to make sure the latest status is present,
        # won't wait for Docdata to call our update API.
        with transaction_atomic():
            self.order = self.get_order(order_key)   # this is the docdata id.
            self.update_order(self.order)

        # Allow other code to perform actions, e.g. send a confirmation email.
        responses = return_view_called.send(sender=self.__class__, request=request, order=self.order, callback=callback)

        # Redirect to thank you page, or the cancelled page,
        # depending on the callback parameter
        with translation.override(self.order.language):   # Allow i18n_patterns() to work properly
            url = str(self.get_redirect_url(callback))    # force evaluation of reverse_lazy()

        return HttpResponseRedirect(url)

    def get_redirect_url(self, callback):
        """
        Return the URL to redirect to.
        The callback value can be 'SUCCESS', 'PENDING', 'CANCELLED', 'ERROR'
        """
        # The callback parameter is added by get_payment_menu_url()
        if callback == 'SUCCESS':
            return self.success_url
        elif callback in ('PENDING', ''):  # treat missing value as pending
            return self.pending_url
        elif callback == 'CANCELLED':
            return self.cancelled_url
        else:
            return self.error_url


class StatusChangedNotificationView(UpdateOrderMixin, View):
    """
    Status changed notification view.

    The URL to this view can be entered in the Docdata backoffice.
    Include the full URL, including ``?order_id=``. The URL is appended with the order ID.
    For example:

    ``http://www.merchantwebsite.com/api/docdata/update_order/?order_id=``

    The use of this service is optional, but recommended.
    """
    order_slug_field = 'merchant_order_id'

    def get(self, request, *args, **kwargs):
        try:
            order_key = self.get_order_slug()
        except KeyError as e:
            return HttpResponseBadRequest(e.message, content_type='text/plain; charset=utf-8')

        logger.info("Got Docdata status changed notification for {0}".format(order_key))

        with transaction_atomic():
            try:
                self.order = self.get_order(order_key)  # Inconsistent, this call uses the merchant_order_id
            except Http404 as e:
                return HttpResponseNotFound(str(e), content_type='text/plain; charset=utf-8')

            try:
                self.update_order(self.order)
            except DocdataStatusError as e:
                logger.exception("The order status could not be retrieved from Docdata by the notification-url")
                return HttpResponseServerError(
                    "Failed to fetch status from Docdata API.\n"
                    "\n\n"
                    "Docdata API response:\n"
                    "---------------------\n"
                    "\n"
                    "code:    {0}\n"
                    "message: {1}".format(e.code, e.message),
                    content_type='text/plain; charset=utf-8'
                )

        responses = status_changed_view_called.send(sender=self.__class__, request=request, order=self.order)

        # Return 200 as required by DocData when the status changed notification was consumed.
        return HttpResponse(u"ok, order updated", content_type='text/plain; charset=utf-8')
