"""
Settings for this application
"""
from django.conf import settings

# Credentials as supplied by the payment provider.
from django.core.urlresolvers import reverse_lazy

DOCDATA_MERCHANT_NAME = getattr(settings, 'DOCDATA_MERCHANT_NAME')
DOCDATA_MERCHANT_PASSWORD = getattr(settings, 'DOCDATA_MERCHANT_PASSWORD')

# Whether to use the testing mode, or live mode.
DOCDATA_TESTING = getattr(settings, 'DOCDATA_TESTING', True)

# The default profile that is used to select the available payment methods that can be used to pay this order.
# Note this profile needs to be created in the Docdata Backoffice. By default, there is no profile available,
# but the parameter is required in the API call.
DOCDATA_PROFILE = getattr(settings, 'DOCDATA_PROFILE', 'standard')

# The default expected number of days in which the payment should be processed, or be expired if not paid.
DOCDATA_DAYS_TO_PAY = getattr(settings, 'DOCDATA_DAYS_TO_PAY', 7)

# The default URL to redirect to. Defaults to a django-oscar view, but it can be any view of your choice.
DOCDATA_REDIRECT_URL = getattr(settings, 'DOCDATA_REDIRECT_URL', reverse_lazy('checkout:thank-you'))

# The list of known issuers (banks) for iDEAL
DOCDATA_IDEAL_ISSUERS = getattr(settings, 'DOCDATA_IDEAL_ISSUERS', {
    '0081': 'Fortis',
    '0021': 'Rabobank',
    '0721': 'ING Bank',
    '0751': 'SNS Bank',
    '0031': 'ABN Amro Bank',
    '0761': 'ASN Bank',
    '0771': 'SNS Regio Bank',
    '0511': 'Triodos Bank',
    '0091': 'Friesland Bank',
    '0161': 'van Lanschot Bankiers'
})
