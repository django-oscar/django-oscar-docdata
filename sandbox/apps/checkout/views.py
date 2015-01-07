import logging
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView
from oscar.apps.payment.exceptions import RedirectRequired
from oscar.apps.checkout import views as oscar_views
from oscar.apps.payment.models import SourceType, Source

from . import forms
from .docdata import CustomDocdataFacade

logger = logging.getLogger(__name__)


class PaymentMethodView(oscar_views.PaymentMethodView, FormView):
    """
    Updated payment methods view.
    """
    template_name = "checkout/payment_method.html"
    step = 'payment-method'
    form_class = forms.PaymentMethodForm
    success_url = reverse_lazy('checkout:payment-details')

    def get_success_response(self):
        # No errors in get(), apply our form logic.
        # NOTE that the checks are not make in the post() call, but this is not a problem.
        # We can just store the payment method, and let the next view validate the other states again.
        return FormView.get(self, self.request, self.args, self.kwargs)

    def get_initial(self):
        return {
            'payment_method': self.checkout_session.payment_method(),
        }

    def form_valid(self, form):
        # Store payment method in the CheckoutSessionMixin.checkout_session (a CheckoutSessionData object)
        self.checkout_session.pay_by(form.cleaned_data['payment_method'])
        return super(PaymentMethodView, self).form_valid(form)


class PaymentDetailsView(oscar_views.PaymentDetailsView):
    """
    The final step to submit the payment.
    This includes an additional form to input comments, and proceeds to the payment provider.
    This connects to the django-oscar-docdata package to start the payment.
    """

    def get_context_data(self, **kwargs):
        context = super(PaymentDetailsView, self).get_context_data(**kwargs)
        method = self.checkout_session.payment_method()
        context['payment_method'] = {
            'code': method,
            'title': forms.get_payment_method_display(method),
        }
        return context


    def handle_place_order_submission(self, request):
        # Collect all the data!
        submission = self.build_submission()

        # docdata needs to have a lot of information to start the payment.
        # TODO: Is this the right way to pass the information??
        submission['payment_kwargs']['submission'] = submission

        # Start the payment process!
        # This jumps to handle_payment()
        return self.submit(**submission)


    def handle_payment(self, order_number, total, **kwargs):
        submission = kwargs['submission']

        # Make request to Docdata.
        # Any raised exceptions are handled by the PaymentDetail.submit() code.
        facade = CustomDocdataFacade()
        docdata_ref = facade.create_payment(
            order_number=order_number,
            total=total,
            user=submission['user'],
            # Extra parameters to add the "Invoice" element in Docdata:
            billing_address=submission['shipping_address'],  # NOTE: no billing address collected in steps.
            shipping_address=submission['shipping_address'],
            basket=submission['basket'],
            description=''
        )

        # NOTE: at this point, the payment is registered as the gateway,
        # and there is no way back. Any errors after this part require manual intervention!

        # Request was successful - record the "payment source".
        # This represents the origin where the payment should come from.
        # When an order is paid in multiple parts, multiple Source objects should be created.
        # As this request was a 'pre-auth', we set the 'amount_allocated'.
        # If we had performed an 'auth' request, then we would set 'amount_debited'.
        source = Source(
            source_type=facade.get_source_type(),
            currency=total.currency,
            amount_allocated=total.incl_tax,   # amount_* field depends on type of transaction.
            reference=docdata_ref
        )
        self.add_payment_source(source)

        # Also record payment event.
        # This will be visible in the Dashboard
        self.add_payment_event('pre-auth', total.incl_tax, reference=docdata_ref)

        # Ask oscar to redirect to docdata
        # TODO: test default_act="yes", skips menu entirely
        # TODO: add issuer_id for iDEAL.
        url = facade.get_payment_menu_url(self.request, docdata_ref, default_pm=self.checkout_session.payment_method())
        logger.info("Redirecting user to {0}".format(url))

        # Regardless of whether the order is paid, write it in the database before redirecting.
        # Oscar actually skips this when redirecting the user to the payment provider.
        self._save_order(order_number, submission)

        # Redirect the user to the payment provider.
        raise RedirectRequired(url)


    def _save_order(self, order_number, submission):
        # Finalize the order that PaymentDetailsView.submit() started
        # If all is ok with payment, try and place order
        logger.info(u"Order #%s: payment started, placing order", order_number)

        try:
            # Call OrderPlacementMixin.handle_order_placement()
            return self.handle_order_placement(
                order_number, submission['user'], submission['basket'], submission['shipping_address'], submission['shipping_method'],
                submission['order_total'], **(submission['order_kwargs'])
            )
        except oscar_views.UnableToPlaceOrder as e:
            # It's possible that something will go wrong while trying to
            # actually place an order.  Not a good situation to be in as a
            # payment transaction may already have taken place, but needs
            # to be handled gracefully.
            logger.error(u"Order #%s: unable to place order - %s", order_number, e, exc_info=True)
            msg = unicode(e)
            self.restore_frozen_basket()
            return self.render_to_response(self.get_context_data(error=msg))

    def send_confirmation_message(self, order, **kwargs):
        # Yes the order is already saved, because this is needed for Docdata.
        # However, delay sending the order confirmation!
        pass
