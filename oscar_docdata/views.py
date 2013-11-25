import logging
from django.http import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse, HttpResponseNotFound, Http404
from django.utils import translation
from django.views.generic import View
from oscar.core.loading import get_class
from oscar_docdata import appsettings
from oscar_docdata.facade import Facade
from oscar_docdata.models import DocdataOrder

logger = logging.getLogger(__name__)

OrderPlacementMixin = get_class('checkout.mixins', 'OrderPlacementMixin')


class UpdateOrderMixin(object):
    """
    Base mixin for updating the order from the API or return URL.
    """

    # What docdata calls the order_id, we call the order_key
    order_key_arg = 'order_id'
    facade_class = Facade

    def get_order_key(self):
        try:
            return self.request.GET[self.order_key_arg]
        except KeyError:
            return HttpResponseBadRequest(u"Missing key parameter", content_type='text/plain; charset=utf-8')

    def update_order(self, order_key):
        # Ask the facade to request the status, and update the order accordingly.
        facade = self.facade_class()

        try:
            return facade.update_order_by_key(order_key)
        except DocdataOrder.DoesNotExist:
            raise Http404(u"Order '{0}' not found!".format(order_key))


class OrderReturnView(UpdateOrderMixin, OrderPlacementMixin, View):
    """
    The view to redirect to after a successful order creation.
    """
    redirect_url = appsettings.DOCDATA_REDIRECT_URL

    def get(self, request, *args, **kwargs):
        order_key = self.get_order_key()
        self.order = self.update_order(order_key)

        # Redirect to thank you page
        with translation.override(self.order.language):                # Allow i18n_patterns() to work properly
            return HttpResponseRedirect(str(self.get_redirect_url()))  # force evaluation of reverse_lazy()

    def get_redirect_url(self):
        return self.redirect_url


class StatusChangedNotificationView(UpdateOrderMixin, View):
    """
    Status changed notification view.

    The URL to this view can be entered in the Docdata backoffice.
    Include the full URL, including ``?order_id=``. The URL is appended with the order ID.
    For example:

    ``http://www.merchantwebsite.com/api/docdata/update_order/?order_id=``

    The use of this service is optional, but recommended.
    """
    def get(self, request, *args, **kwargs):
        order_key = self.get_order_key()
        try:
            self.update_order(order_key)
        except Http404 as e:
            return HttpResponseNotFound(str(e), content_type='text/plain; charset=utf-8')

        # Return 200 as required by DocData when the status changed notification was consumed.
        return HttpResponse(u"ok, order updated", content_type='text/plain; charset=utf-8')
