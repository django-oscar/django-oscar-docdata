from django.contrib.auth import get_user_model
from django.core.management import call_command

from oscar.core.loading import get_model

from oscar_docdata.gateway import DocdataAPIVersionPlugin

import pytest

import suds

from .suds_transport import DocdataMockTransport

User = get_user_model()

Country = get_model('address', 'Country')
UserAddress = get_model('address', 'UserAddress')
SourceType = get_model('payment', 'SourceType')

pytest_plugins = "tests.fixtures"


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # load a country so we can fill out a shipping address
        call_command("loaddata", "sandbox/fixtures/countries.json")

        # loads books so we have products to do a checkout with
        call_command("oscar_import_catalogue", "sandbox/fixtures/books.csv")

        # add a customer to login with
        user = User(username="customer", email="customer@oscarcommerce.com")
        user.set_password("customer")
        user.save()

        # and a address so we can checkout
        UserAddress.objects.create(
            user=user, title="Mr", first_name="John", last_name="Doe", line1="Just a street 1",
            line4="Amsterdam", postcode="1111AA", country=Country.objects.get(pk="NL"))

        # add a docdata payment sourcetype
        SourceType.objects.create(name="Docdata Payments", code="docdata")


@pytest.fixture(autouse=True)
def mock_suds(mocker):
    url = 'https://test.docdatapayments.com/ps/services/paymentservice/1_2?wsdl'

    # create a custom suds client with a wsdl and xsd saved on disk so we don't really connect
    # to docdata
    client = suds.client.Client(
        url, plugins=[DocdataAPIVersionPlugin()], transport=DocdataMockTransport())
    client.options.prettyxml = True

    # patch the CACHED_CLIENT so get_suds_client will return ours
    mocker.patch.dict("oscar_docdata.gateway.CACHED_CLIENT", {url: client})
