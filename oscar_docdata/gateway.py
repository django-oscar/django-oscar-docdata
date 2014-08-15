"""
Backend calls to docdata.

Gateway module - this module is ignorant of Oscar and could be used in a non-Oscar project.
All Oscar-related functionality should be in the facade.
"""
import logging
from django.core.exceptions import ImproperlyConfigured
import suds
import suds.plugin
from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from urllib import urlencode
from urllib2 import URLError
from oscar_docdata import appsettings, __version__ as oscar_docdata_version
from oscar_docdata.exceptions import DocdataCreateError, DocdataStatusError, DocdataStartError, DocdataCancelError, OrderKeyMissing

logger = logging.getLogger(__name__)

__all__ = (
    'DocdataClient',

    'CreateReply',
    'StartReply',
    'StatusReply',

    'Name',
    'Shopper',
    'Destination',
    'Address',
    'Amount',

    'Payment',
    'AmexPayment',
    'MasterCardPayment',
    'DirectDebitPayment',
    'IdealPayment',
    'BankTransferPayment',
    'ElvPayment',
)


# Thanks to https://github.com/onepercentclub/onepercentclub-site for an example implmentation,
# which is BSD licensed, copyright (c) 2013 1%CLUB and Ben Konrath.


# Getting call metadata:
#
# >>> from suds.client import Client
# >>> url = 'https://test.docdatapayments.com/ps/services/paymentservice/1_0?wsdl'
# >>> client = Client(url)
#
# >>> print client
#
# >>> client.factory.create('ns0:name')


def get_suds_client(testing_mode=False):
    """
    Create the suds client to connect to docdata.
    """
    if testing_mode:
        url = 'https://test.docdatapayments.com/ps/services/paymentservice/1_2?wsdl'
    else:
        url = 'https://secure.docdatapayments.com/ps/services/paymentservice/1_2?wsdl'

    # TODO: CACHE THIS object, avoid having to request the WSDL at every instance.
    try:
        return suds.client.Client(url, plugins=[DocdataAPIVersionPlugin()])
    except URLError as e:
        logger.error('{0} {1}'.format("Could not initialize SUDS SOAP client to connect to Docdata", str(e)))
        raise


class DocdataAPIVersionPlugin(suds.plugin.MessagePlugin):
    """
    This adds the API version number to the body element. This is required for the Docdata soap API.
    """

    def marshalled(self, context):
        body = context.envelope.getChild('Body')
        request = body[0]
        request.set('version', '1.2')


#class DocdataBrokenWSDLPlugin(suds.plugin.DocumentPlugin):
#    def parsed(self, context):
#        """ Called after parsing a WSDL or XSD document. The context contains the url & document root. """
#        # The WSDL for the live payments API incorrectly references the wrong location.
#        if len(context.document.children) == 19 and len(context.document.children[18]) > 0:
#            location_attribute = context.document.children[18].children[0].getChild('address').attributes[0]
#            location_attribute.setValue('https://secure.docdatapayments.com:443/ps/services/paymentservice/1_0')


def log_docdata_error(error, message):
    logger.error(u"{0}: code={1}, error={2}".format(message, error._code, error.value))


class DocdataClient(object):
    """
    API Client for docdata.

    This is a wrapper around the SOAP service methods,
    providing more Python-friendly wrappers.
    """

    # Status values. Besides the regular ones mentioned in the documentation,
    # the WSDL also mentions additional status values for the authorizationStatus enum.
    # The CANCELLED statuses are actually misspelled in the protocol.
    STATUS_NEW = 'NEW'

    STATUS_RISK_CHECK_OK = 'RISK_CHECK_OK'
    STATUS_RISK_CHECK_FAILED = 'RISK_CHECK_FAILED'

    STATUS_STARTED = 'STARTED'
    STATUS_START_ERROR = 'START_ERROR'

    STATUS_AUTHENTICATED = 'AUTHENTICATED'
    STATUS_REDIRECTED_FOR_AUTHENTICATION = 'REDIRECTED_FOR_AUTHENTICATION'
    STATUS_AUTHENTICATION_FAILED = 'AUTHENTICATION_FAILED'
    STATUS_AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR'

    STATUS_AUTHORIZED = 'AUTHORIZED'
    STATUS_REDIRECTED_FOR_AUTHORIZATION = 'REDIRECTED_FOR_AUTHORIZATION'
    STATUS_AUTHORIZATION_REQUESTED = 'AUTHORIZATION_REQUESTED'
    STATUS_AUTHORIZATION_FAILED = 'AUTHORIZATION_FAILED'
    STATUS_AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR'

    STATUS_PAID = 'PAID'

    STATUS_CANCELLED = 'CANCELED'  # Typoo in protocol, not mentioned in the docs
    STATUS_CANCEL_FAILED = 'CANCEL_FAILED'
    STATUS_CANCEL_ERROR = 'CANCEL_ERROR'
    STATUS_CANCEL_REQUESTED = 'CANCEL_REQUESTED'

    STATUS_CHARGED_BACK = 'CHARGED-BACK'
    STATUS_CONFIRMED_PAID = 'CONFIRMED_PAID'
    STATUS_CONFIRMED_CHARGEDBACK = 'CONFIRMED_CHARGEDBACK'
    STATUS_CLOSED_SUCCESS = 'CLOSED_SUCCESS'
    STATUS_CLOSED_CANCELLED = 'CLOSED_CANCELED'  # Typoo in protocol

    DOCUMENTED_STATUS_VALUES = (
        STATUS_NEW,
        STATUS_STARTED,
        STATUS_REDIRECTED_FOR_AUTHENTICATION,
        STATUS_AUTHORIZED,
        STATUS_AUTHORIZATION_REQUESTED,
        STATUS_PAID,
        STATUS_CANCELLED,
        STATUS_CHARGED_BACK,
        STATUS_CONFIRMED_PAID,
        STATUS_CONFIRMED_CHARGEDBACK,
        STATUS_CLOSED_SUCCESS,
        STATUS_CLOSED_CANCELLED,
    )

    SEEN_UNDOCUMENTED_STATUS_VALUES = (
        STATUS_AUTHORIZATION_FAILED,
        STATUS_CANCEL_FAILED,
        STATUS_AUTHORIZATION_ERROR,
    )

    # Payment methods for the start operation.
    PAYMENT_METHOD_AMEX = 'AMEX'
    PAYMENT_METHOD_MASTERCARD = 'MASTERCARD'
    PAYMENT_METHOD_VISA = 'VISA'
    PAYMENT_METHOD_DIRECT_DEBIT = 'DIRECT_DEBIT'
    PAYMENT_METHOD_BANK_TRANSFER = 'BANK_TRANSFER'
    PAYMENT_METHOD_ELV = 'ELV'


    def __init__(self, testing_mode=None):
        """
        Initialize the client.
        """
        if testing_mode is None:
            testing_mode = appsettings.DOCDATA_TESTING

        self.testing_mode = testing_mode
        self.client = get_suds_client(testing_mode)

        if not appsettings.DOCDATA_MERCHANT_NAME:
            raise ImproperlyConfigured("Missing DOCDATA_MERCHANT_NAME setting!")
        if not appsettings.DOCDATA_MERCHANT_PASSWORD:
            raise ImproperlyConfigured("Missing DOCDATA_MERCHANT_PASSWORD setting!")

        # Create the merchant node which is passed to every request.
        # The _ notation is used to assign attributes to the XML node, instead of child elements.
        self.merchant = self.client.factory.create('ns0:merchant')
        self.merchant._name = appsettings.DOCDATA_MERCHANT_NAME
        self.merchant._password = appsettings.DOCDATA_MERCHANT_PASSWORD

        # Create the integration info node which is passed to every request.
        self.integration_info = TechnicalIntegrationInfo()


    def create(self,
            order_id,
            total_gross_amount,
            shopper,
            bill_to,
            description,
            receiptText=None,
            includeCosts=False,
            profile=appsettings.DOCDATA_PROFILE,
            days_to_pay=appsettings.DOCDATA_DAYS_TO_PAY,
        ):
        """
        Create the payment in docdata.

        This is the first step of any payment session.
        After the payment is created, an ``order_key`` will be used.
        This key can be used to continue using the Payment Menu,
        or make the next call to start a Web Direct payment.

        The goal of the create operation is solely to create a payment order on Docdata Payments system.
        Creating a payment order is always the first step of any workflow in Docdata Payments payment service.

        After an order is created, payments can be made on this order; either through (the shopper via) the web menu
        or through the API by the merchant. If the order has been created using information on specific order items,
        the web menu can make use of this information by displaying a shopping cart.

        :param order_id: Unique merchant reference to this order.
        :type total_gross_amount: Amount
        :param shopper: Information concerning the shopper who placed the order.
        :type shopper: Shopper
        :param bill_to: Name and address to use for billing.
        :type bill_to: Destination
        :param description: The description of the order (max 50 chars).
        :type description: str
        :param receiptText: The description that is used by payment providers on shopper statements (max 50 chars).
        :type receiptText: str
        :param profile: The profile that is used to select the payment methods that can be used to pay this order.
        :param days_to_pay: The expected number of days in which the payment should be processed, or be expired if not paid.
        :rtype: CreateReply
        """
        # Preferences for the DocData system.
        paymentPreferences = self.client.factory.create('ns0:paymentPreferences')
        paymentPreferences.profile = profile
        paymentPreferences.numberOfDaysToPay = days_to_pay
        # paymentPreferences.exhortation.period1 ?
        # paymentPreferences.exhortation.period2 ?

        # Menu preferences are empty. They are used for CSS file selection in the payment menu.
        menuPreferences = self.client.factory.create('ns0:menuPreferences')

        # Execute create payment order request.
        #
        # create(
        #     merchant merchant, string35 merchantOrderReference, paymentPreferences paymentPreferences,
        #     menuPreferences menuPreferences, shopper shopper, amount totalGrossAmount,
        #     destination billTo, string50 description, string50 receiptText, xs:boolean includeCosts,
        #     paymentRequest paymentRequest, invoice invoice )
        #
        # The WSDL and XSD also contain documentation individualnvidual parameters:
        # https://secure.docdatapayments.com/ps/services/paymentservice/1_0?xsd=1
        #
        # TODO: can also pass shipTo + invoice details to docdata.
        # This displays the results in the docdata web menu.
        #
        reply = self.client.service.create(
            self.merchant, order_id, paymentPreferences, menuPreferences,
            shopper.to_xml(self.client.factory),
            total_gross_amount.to_xml(self.client.factory),
            bill_to.to_xml(self.client.factory),
            description or None,
            receiptText or None,
            includeCosts or False,
            integrationInfo=self.integration_info.to_xml(self.client.factory)
        )

        # Parse the reply
        if hasattr(reply, 'createSuccess'):
            order_key = str(reply['createSuccess']['key'])
            return CreateReply(order_id, order_key)
        elif hasattr(reply, 'createError'):
            error = reply.createError.error
            log_docdata_error(error, "DocdataClient: failed to create payment for order {0}".format(order_id))
            raise DocdataCreateError(error._code, error.value)
        else:
            raise NotImplementedError('Received unknown reply from DocData. Remote Payment not created.')


    def start(self, order_key, payment, payment_method=None, amount=None):
        """
        The start operation is used for starting a (web direct) payment on an order.
        It does not need to be used if the merchant makes use of Docdata Payments web menu.

        The web direct can be used for recurring payments for example.
        Standard payments (e.g. iDEAL, creditcard) all happen through the web menu
        because implementing those locally requires certification by the credit card companies.

        TODO: untested

        :type order_key: str
        :param payment: A subclass of the payment class, which one depends on the payment method.
        :type payment: Payment
        :param payment_method: One of the supported payment methods, e.g. PAYMENT_METHOD_IDEAL, PAYMENT_METHOD_MASTERCARD.
                               If omitted, the payment method of the ``payment`` object is used.
        :type payment_method: str
        :param amount: Optional payment amount. If left empty, the full amount of the payment order is used.
        :type amount: Amount
        """
        if not order_key:
            raise OrderKeyMissing("Missing order_key!")

        # We only need to set amount because of bug in suds library. Otherwise it defaults to order amount.

        paymentRequestInput = self.client.factory.create('ns0:paymentRequestInput')
        if amount is not None:
            paymentRequestInput.paymentAmount = amount.to_xml(self.client.factory)
        paymentRequestInput.paymentMethod = payment_method or payment.payment_method
        paymentRequestInput[payment.request_parameter] = payment.to_xml(self.client.factory)

        # Execute start payment request.
        reply = self.client.service.start(
            self.merchant,
            order_key,
            paymentRequestInput,
            integrationInfo=self.integration_info.to_xml(self.client.factory)
        )
        if hasattr(reply, 'startSuccess'):
            return StartReply(reply.startSuccess.paymentId)
        elif hasattr(reply, 'startError'):
            error = reply.createError.error
            log_docdata_error(error, "DocdataClient: failed to get start payment for order {0}".format(order_key))
            raise DocdataStartError(error._code, error.value)
        else:
            raise NotImplementedError('Received unknown reply from DocData. Remote Payment not created.')


    def cancel(self, order_key):
        """
        The cancel command is used for canceling a previously created payment,
        and can only be used for payments with status NEW, STARTED and AUTHORIZED.
        """
        if not order_key:
            raise OrderKeyMissing("Missing order_key!")

        reply = self.client.service.cancel(self.merchant, order_key)

        if hasattr(reply, 'cancelSuccess'):
            return True
        elif hasattr(reply, 'cancelError'):
            error = reply.cancelError.error
            log_docdata_error(error, "DocdataClient: failed to cancel the order {0}".format(order_key))
            raise DocdataCancelError(error._code, error.value)
        else:
            logger.error("Unexpected response node from docdata!")
            raise NotImplementedError('Received unknown reply from DocData. Remote Payment not cancelled.')


    def status(self, order_key):
        """
        Request the status of of order and it's payments.

        :rtype: StatusReply
        """
        # Example response:
        #
        # <?xml version='1.0' encoding='UTF-8'?>
        # <statusResponse xmlns="http://www.docdatapayments.com/services/paymentservice/1_0/">
        #   <statusSuccess>
        #     <success code="SUCCESS">Operation successful.</success>
        #     <report>
        #       <approximateTotals exchangedTo="EUR" exchangeRateDate="2012-12-04 14:39:53">
        #         <totalRegistered>3310</totalRegistered>
        #         <totalShopperPending>0</totalShopperPending>
        #         <totalAcquirerPending>0</totalAcquirerPending>
        #         <totalAcquirerApproved>3310</totalAcquirerApproved>
        #         <totalCaptured>0</totalCaptured>
        #         <totalRefunded>0</totalRefunded>
        #         <totalChargedback>0</totalChargedback>
        #       </approximateTotals>
        #       <payment>           # Can occur multiple times.
        #         <id>1606709142</id>
        #         <paymentMethod>MASTERCARD</paymentMethod>
        #         <authorization>
        #           <status>AUTHORIZED</status>
        #           <amount currency="EUR">3310</amount>
        #           <confidenceLevel>ACQUIRER_APPROVED</confidenceLevel>
        #         </authorization>
        #       </payment>
        #     </report>
        #   </statusSuccess>
        # </statusResponse>
        if not order_key:
            raise OrderKeyMissing("Missing order_key!")

        reply = self.client.service.status(
            self.merchant,
            order_key,
            iIntegrationInfo=self.integration_info.to_xml(self.client.factory)  # NOTE: called iIntegrationInfo in the XSD!!
        )

        if hasattr(reply, 'statusSuccess'):
            return StatusReply(order_key, reply.statusSuccess.report)
        elif hasattr(reply, 'statusError'):
            error = reply.statusError.error
            log_docdata_error(error, "DocdataClient: failed to get status for order {0}".format(order_key))
            raise DocdataStatusError(error._code, error.value)
        else:
            logger.error("Unexpected response node from docdata!")
            raise NotImplementedError('Received unknown reply from DocData. No status processed from Docdata.')


    def status_extended(self, order_key):
        """
        Request the status with extended information.
        """
        if not order_key:
            raise OrderKeyMissing("Missing order_key!")

        reply = self.client.service.statusExtended(
            self.merchant,
            order_key,
            self.integration_info.to_xml(self.client.factory)  # NOTE: called iIntegrationInfo in the XSD!!
        )

        if hasattr(reply, 'statusSuccess'):
            return StatusReply(order_key, reply.statusSuccess.report)
        elif hasattr(reply, 'statusError'):
            error = reply.statusError.error
            log_docdata_error(error, "DocdataClient: failed to get status for order {0}".format(order_key))
            raise DocdataStatusError(error._code, error.value)
        else:
            logger.error("Unexpected response node from docdata!")
            raise NotImplementedError('Received unknown reply from DocData. Remote Payment not created.')


    def get_payment_menu_url(self, request, order_key, return_url=None, client_language=None, **extra_url_args):
        """
        Return the URL to the payment menu,
        where the user can be redirected to after creating a successful payment.

        Make sure URLs are absolute, and include the hostname and ``https://`` part.

        When using default_act (possible values "yes" or "true") as well as default_pm,
        your shopper will be redirected straight from your shop to the payment page of the payment method.
        This works only with those payment methods that are initiated by a single click,
        PayPal, Rabo SMS-betalen, SofortUberweisung, eBanking, KBC Betaalknop and iDEAL.
        When the issuer_id is added to the redirect string, this works for iDEAL as well.

        :param extra_args: Additional URL arguments, e.g. default_pm=IDEAL, ideal_issuer_id=0021, default_act='true'
        """
        if not return_url:
            return_url = reverse('return_url', current_app='oscar_docdata')

        # Add order_id= parameter to the URL
        if '?' in return_url:
            url_format = '{0}&callback={callback}&order_id={order_id}'
        else:
            url_format = '{0}?callback={callback}&order_id={order_id}'

        # Make sure URLs are absolute.
        if not '://' in return_url or return_url.startswith('/'):
            return_url = request.build_absolute_uri(return_url)

        args = {
            'command': 'show_payment_cluster',
            'payment_cluster_key': order_key,
            'merchant_name': appsettings.DOCDATA_MERCHANT_NAME,
            'return_url_success': url_format.format(return_url, callback='SUCCESS', order_id=order_key),
            'return_url_pending': url_format.format(return_url, callback='PENDING', order_id=order_key),
            'return_url_canceled': url_format.format(return_url, callback='CANCELLED', order_id=order_key),
            'return_url_error': url_format.format(return_url, callback='ERROR', order_id=order_key),
            'client_language': (client_language or get_language()).upper()
        }
        args.update(extra_url_args)

        if self.testing_mode:
            return 'https://test.docdatapayments.com/ps/menu?' + urlencode(args)
        else:
            return 'https://secure.docdatapayments.com/ps/menu?' + urlencode(args)



class CreateReply(object):
    """
    Docdata response for the create request
    """
    def __init__(self, order_id, order_key):
        # In this library, we favor explicit reply objects over dictionaries,
        # because it makes it much more explicit what is being returned.
        # BTW, PyPy also loves this ;) Much easier to optimize then dict lookups.
        self.order_id = order_id
        self.order_key = order_key

    def __repr__(self):
        return "<CreateReply {0}>".format(self.order_key)


class StartReply(object):
    """
    Docdata response for the start request.
    """
    def __init__(self, payment_id):
        self.payment_id = payment_id

    def __repr__(self):
        return "<StartReply {0}>".format(self.payment_id)


class StatusReply(object):
    """
    Docdata response for the status request.
    """
    def __init__(self, order_key, report):
        self.order_key = order_key
        self.report = report

    def __repr__(self):
        return "<StatusReply {0}>".format(repr(self.report))


class Name(object):
    """
    A name for Docdata.

    :type first: unicode
    :type last: unicode
    :type middle: unicode
    :type initials: unicode
    :type prefix: unicode
    :type suffix: unicode
    """
    def __init__(self, first, last, middle=None, initials=None, prefix=None, suffix=None):
        if not last:
            raise ValueError("Name.last is required!")
        if not first:
            raise ValueError("Name.first is required!")
        self.first = first
        self.last = last
        self.prefix = prefix
        self.initials = initials
        self.middle = middle
        self.suffix = suffix

    def to_xml(self, factory):
        # Assigning values is perhaps very Java-esque, but it's very obvious too
        # what's happening here, while keeping Python-like constructor argument styles.
        node = factory.create('ns0:name')
        node.first = unicode(self.first)
        node.middle = unicode(self.middle) if self.middle else None
        node.last = unicode(self.last)
        node.initials = unicode(self.initials) if self.initials else None
        node.prefix = unicode(self.prefix) if self.prefix else None
        node.suffix = unicode(self.suffix) if self.suffix else None
        return node


class Shopper(object):
    """
    Information concerning the shopper who placed the order.

    :type id: long
    :type name: Name
    :type email: str
    :type language: str
    :type gender: str
    :type date_of_birth: :class:`datetime.Date`
    :type phone_number: str
    :type mobile_phone_number: str
    """
    def __init__(self, id, name, email, language, gender="U", date_of_birth=None, phone_number=None, mobile_phone_number=None, ipAddress=None):
        """
        :type name: Name
        """
        self.id = id
        self.name = name
        self.email = email
        self.language = language
        self.gender = gender   # M (male), F (female), U (undefined)
        self.date_of_birth = date_of_birth
        self.phone_number = phone_number
        self.mobile_phone_number = mobile_phone_number  # +316..
        self.ipAddress = ipAddress

    def to_xml(self, factory):
        language_node = factory.create('ns0:language')
        language_node._code = self.language

        node = factory.create('ns0:shopper')
        node._id = self.id  # attribute, hence the ._id
        node.name = self.name.to_xml(factory)
        node.gender = self.gender.upper() if self.gender else "U"
        node.language = language_node
        node.email = self.email
        node.dateOfBirth = self.date_of_birth.isoformat() if self.date_of_birth else None   # yyyy-mm-dd
        node.phoneNumber = self.phone_number                # string50, must start with "+"
        node.mobilePhoneNumber = self.mobile_phone_number   # string50, must start with "+"
        node.ipAddress = self.ipAddress if self.ipAddress else None
        return node


class Destination(object):
    """
    Name and address to use for billing.
    """
    def __init__(self, name, address):
        """
        :type name: Name
        :type address: Address
        """
        self.name = name
        self.address = address

    def to_xml(self, factory):
        node = factory.create('ns0:destination')
        node.name = self.name.to_xml(factory)
        node.address = self.address.to_xml(factory)
        return node


class Address(object):
    """
    An address for docdata

    :type street: unicode
    :type house_number: str
    :type house_number_addition: unicode
    :type postal_code: str
    :type city: unicode
    :type state: unicode
    :type country_code: str
    :type company: unicode
    :type vatNumber: unicode
    :type careOf: unicode
    """
    def __init__(self, street, house_number, house_number_addition, postal_code, city, state, country_code, company=None, vatNumber=None, careOf=None):
        self.street = street
        self.house_number = house_number
        self.house_number_addition = house_number_addition
        self.postal_code = postal_code
        self.city = city
        self.state = state
        self.country_code = country_code

        self.company = company
        self.vatNumber = vatNumber
        self.careOf = careOf
        #self.kvkNummer    # rant: seriously? a Netherlands-specific field in the API?

    def to_xml(self, factory):
        country = factory.create('ns0:country')
        country._code = unicode(self.country_code)

        node = factory.create('ns0:address')
        node.street = unicode(self.street)
        node.houseNumber = unicode(self.house_number)  #string35
        node.houseNumberAddition = unicode(self.house_number_addition) if self.house_number_addition else None
        node.postalCode = unicode(self.postal_code.replace(' ', ''))  # Spaces aren't allowed in the Docdata postal code (type=NMTOKEN)
        node.city = unicode(self.city)
        node.state = unicode(self.state) if self.state else None
        node.country = country

        # Optional company info
        node.company = unicode(self.company) if self.company else None
        node.vatNumber = unicode(self.vatNumber) if self.vatNumber else None
        node.careOf = unicode(self.careOf) if self.careOf else None
        return node


class Amount(object):
    """
    An amount for Docdata.
    """
    def __init__(self, value, currency):
        self.value = value
        self.currency = currency

    def to_xml(self, factory):
        node = factory.create('ns0:amount')
        node.value = int(self.value * 100)   # No comma!
        node._currency = self.currency       # An attribute
        return node


class TechnicalIntegrationInfo(object):
    """
    Pass integration information to the API for debugging assistance.
    """
    def to_xml(self, factory):
        node = factory.create('ns0:technicalIntegrationInfo')
        node.webshopPlugin = "django-oscar-docdata"
        node.webshopPluginVersion = oscar_docdata_version
        node.programmingLanguage = "Python"
        return node


class Payment(object):
    """
    Base interface for all payment inputs.
    """
    payment_method = None
    request_parameter = None

    def to_xml(self, factory):
        raise NotImplementedError("Missing to_xml() implementation in {0}".format(self.__class__.__name__))


class AmexPayment(Payment):
    """
    American Express payment.
    """
    payment_method = DocdataClient.PAYMENT_METHOD_AMEX
    request_parameter = 'amexPaymentInput'

    def __init__(self, credit_card_number, expiry_date, cid, card_holder, email_address):
        self.credit_card_number = credit_card_number
        self.expiry_date = expiry_date
        self.cid = cid
        self.card_holder = card_holder
        self.email_address = email_address

    def to_xml(self, factory):
        node = factory.create('ns0:amexPaymentInput')
        node.creditCardNumber = self.credit_card_number
        node.expiryDate = self.expiry_date
        node.cid = self.cid
        node.cardHolder = unicode(self.card_holder)
        node.emailAddress = self.email_address
        return node


class MasterCardPayment(Payment):
    """
    Mastercard payment
    """
    payment_method = DocdataClient.PAYMENT_METHOD_MASTERCARD
    request_parameter = 'masterCardPaymentInput'

    def __init__(self, credit_card_number, expiry_date, cvc2, card_holder, email_address):
        self.credit_card_number = credit_card_number
        self.expiry_date = expiry_date
        self.cvc2 = cvc2
        self.card_holder = unicode(card_holder)
        self.email_address = email_address

    def to_xml(self, factory):
        node = factory.create('ns0:masterCardPaymentInput')
        node.creditCardNumber = self.credit_card_number
        node.expiryDate = self.expiry_date
        node.cvc2 = self.cvc2
        node.cardHolder = unicode(self.card_holder)
        node.emailAddress = self.email_address
        return node


class DirectDebitPayment(Payment):
    """
    Direct debit payment.
    """
    payment_method = DocdataClient.PAYMENT_METHOD_DIRECT_DEBIT
    request_parameter = 'directDebitPaymentInput'

    def __init__(self, holder_name, holder_city, holder_country_code, bic, iban):
        self.holder_name = holder_name
        self.holder_city = holder_city
        self.holder_country_code = holder_country_code
        self.bic = bic
        self.iban = iban

    def to_xml(self, factory):
        country = factory.create('ns0:country')
        country._code = self.holder_country_code

        node = factory.create('ns0:directDebitPaymentInput')
        node.holderName = unicode(self.holder_name)
        node.holderCity = unicode(self.holder_city)
        node.holderCountry = country
        node.bic = self.bic
        node.iban = self.iban
        return node


class IdealPayment(DirectDebitPayment):
    """
    Direct debit payment in The Netherlands.
    The visitor is redirected to the bank website where the payment is made,
    and then redirected back to the gateway.
    """
    payment_method = 'IDEAL'


class BankTransferPayment(Payment):
    """
    Bank transfer.
    https://support.docdatapayments.com/index.php?_m=knowledgebase&_a=viewarticle&kbarticleid=141&nav=0,7
    """
    payment_method = DocdataClient.PAYMENT_METHOD_BANK_TRANSFER
    request_parameter = 'bankTransferPaymentInput'

    def __init__(self, email_address):
        self.email_address = email_address

    def to_xml(self, factory):
        node = factory.create('ns0:bankTransferPaymentInput')
        node.emailAddress = self.email_address
        return node


class ElvPayment(Payment):
    """
    The German Electronic Direct Debit (Elektronisches Lastschriftverfahren or ELV)
    """
    payment_method = DocdataClient.PAYMENT_METHOD_ELV
    request_parameter = 'elvPaymentInput'

    def __init__(self, account_number, bank_code):
        self.account_number = account_number
        self.bank_code = bank_code

    def to_xml(self, factory):
        node = factory.create('ns0:elvPaymentInput')
        node.accountNumber = self.account_number
        node.bankCode = self.bank_code
        return node
