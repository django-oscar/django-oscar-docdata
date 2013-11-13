"""
Bridging module between Oscar and the gateway module (which is Oscar agnostic)
"""
from django.utils.translation import get_language
from oscar.apps.payment.exceptions import PaymentError
from oscar_docdata import appsettings
from oscar_docdata.exceptions import DocdataCreateError
from oscar_docdata.gateway import Name, Shopper, Destination, Address, Amount
from oscar_docdata.interface import Interface


class Facade(Interface):
    """
    The bridge between Oscar and the generic Interface.

    Most methods are just called directly on the Interface.
    """

    def create_payment(self, order_number, total, user, language=None, description=None, profile=appsettings.DOCDATA_PROFILE, **kwargs):
        """
        Start a new payment session / container.
        Becides the overwritten parameters, also provide:

        :param billingaddress: The shipping address.
        :type billingaddress: :class:`oscar.apps.order.models.BillingAddress`
        """
        try:
            order_key = super(Facade, self).create_payment(order_number, total, user, language=language, description=description, profile=profile, **kwargs)
        except DocdataCreateError as e:
            raise PaymentError(e.value, e)
        except ValueError as e:
            raise PaymentError(str(e))

        # TODO: create Oscar PaymentEvent?

        return order_key



    def get_create_payment_args(self, order_number, total, user, language=None, description=None, profile=appsettings.DOCDATA_PROFILE, **kwargs):
        """
        The arguments for the createpayment call.
        """
        billingaddress = kwargs['billingaddress']

        # Separate method to be easily overwritable.
        if user.first_name and user.last_name:
            shopper_name = Name(
                first=user.first_name,
                last=user.last_name
            )
        else:
            shopper_name = Name(
                first=billingaddress.first_name,
                last=billingaddress.last_name
            )

        return dict(
            order_id=order_number,
            total_gross_amount=Amount(total.incl_tax, total.currency),
            shopper=Shopper(
                id=user.id,
                name=shopper_name,
                email=user.email,
                language=language or get_language(),
                gender='U'
            ),
            bill_to=Destination(
                shopper_name,
                address=Address(
                    street=billingaddress.line1,            # NOTE: oscar has no street / housenumber fields!
                    house_number='N/A',
                    house_number_addition=None,
                    postal_code=billingaddress.postcode,
                    city=billingaddress.city,
                    country_code=billingaddress.country_id  # The Country.iso_3166_1_a2 field.
                )
            ),
            description=description,
            profile=profile
        )
