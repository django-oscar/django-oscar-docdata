from oscar.apps.checkout import app
from sandbox.apps.checkout import views


class CheckoutApplication(app.CheckoutApplication):
    # Specify new view for payment details
    payment_method_view = views.PaymentMethodView
    payment_details_view = views.PaymentDetailsView


application = CheckoutApplication()
