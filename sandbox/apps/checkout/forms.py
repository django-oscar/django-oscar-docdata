from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class PaymentMethodForm(forms.Form):
    """
    Extra form for the custom payment method.
    """
    payment_method = forms.ChoiceField(
        label=_("Choose your payment method"),
        choices=settings.WEBSHOP_PAYMENT_CHOICES,
        widget=forms.RadioSelect()
    )


def get_payment_method_display(payment_method):
    return dict(settings.WEBSHOP_PAYMENT_CHOICES).get(payment_method)
