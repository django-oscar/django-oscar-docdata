from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.http import  HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView, View, DeleteView
from django.views.generic.detail import SingleObjectMixin
from oscar_docdata.exceptions import DocdataStatusError, DocdataCancelError
from oscar_docdata.facade import get_facade
from oscar_docdata.models import DocdataOrder
from .forms import DocdataOrderSearchForm


class DocdataOrderListView(ListView):
    """
    List of orders
    """
    model = DocdataOrder
    template_name = 'oscar_docdata/dashboard/orders/list.html'
    form_class = DocdataOrderSearchForm
    paginate_by = 25

    def get_queryset(self):
        """
        Build the queryset for this list.
        """
        qs = super(DocdataOrderListView, self).get_queryset()

        # Always show the current merchant only.
        # Can't use the the API calls for different merchants anyway,
        # and this makes it possible to use a multi-tenant site.
        qs = qs.active_merchants()

        # Look for shortcut query filters
        if 'order_number' in self.request.GET or 'order_status' in self.request.GET:
            self.form = self.form_class(self.request.GET)
            if not self.form.is_valid():
                return qs

            data = self.form.cleaned_data
            status = data.get('order_status')
            number = data.get('order_number')

            if number:
                qs = qs.filter(Q(merchant_order_id__contains=number) | Q(order_key__contains=number))
            if status:
                qs = qs.filter(status=status)
        else:
            self.form = self.form_class()

        return qs

    def get_context_data(self, **kwargs):
        ctx = super(DocdataOrderListView, self).get_context_data(**kwargs)
        ctx['form'] = self.form
        return ctx


class DocdataOrderDetailView(DetailView):
    """
    Detail view
    """
    model = DocdataOrder
    template_name = 'oscar_docdata/dashboard/orders/detail.html'
    success_url = reverse_lazy('docdata-order-list')

    def get_context_data(self, **kwargs):
        ctx = super(DocdataOrderDetailView, self).get_context_data(**kwargs)
        ctx['object_payments'] = self.object.payments.all()
        return ctx


class DocdataOrderUpdateStatusView(SingleObjectMixin, View):
    """
    Update the order status
    """
    model = DocdataOrder

    def get(self, request, *args, **kwargs):
        """
        Fetch the latest status from docdata.
        """
        self.object = self.get_object()

        # Perform update.
        try:
            facade = get_facade()
            facade.update_order(self.object)
        except DocdataStatusError as e:
            messages.error(request, e.value)
        else:
            messages.info(request, u"Order status is updated")

        return HttpResponseRedirect(reverse('docdata-order-detail', args=(self.object.pk,)))


class DocdataOrderCancelView(DeleteView):
    """
    Update the order status
    """
    model = DocdataOrder
    template_name_suffix = "_confirm_cancel"
    template_name = 'oscar_docdata/dashboard/orders/confirm_cancel.html'

    def delete(self, request, *args, **kwargs):
        """
        Cancel the object in Docdata
        """
        self.object = self.get_object()

        # Perform cancel
        try:
            facade = get_facade()
            facade.cancel_order(self.object)
        except DocdataCancelError as e:
            messages.error(request, e.value)
        else:
            messages.info(request, _(u'The order "{order_id}" was cancelled successfully.').format(order_id=self.object.merchant_order_id))

        return HttpResponseRedirect(reverse('docdata-order-detail', args=(self.object.pk,)))
