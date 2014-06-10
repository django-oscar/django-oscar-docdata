from oscar.apps.checkout.app import CheckoutApplication as OscarCheckoutApplication
from apps.checkout import views


class CheckoutApplication(OscarCheckoutApplication):
    # Specify new view for payment details
    payment_method_view = views.PaymentMethodView
    payment_details_view = views.PaymentDetailsView


application = CheckoutApplication()
