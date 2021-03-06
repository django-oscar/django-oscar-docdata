import os
import tempfile

from django.core.management import call_command

from oscar_docdata.gateway import DocdataAPIVersionPlugin

import pytest

import suds

from .suds_transport import DocdataMockTransport

pytest_plugins = "tests.fixtures"


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # load a country so we can fill out a shipping address
        call_command("loaddata", "sandbox/fixtures/countries.json")

        # import one book from the sandbox csv data
        csv_data = open("sandbox/fixtures/books.csv").readlines()
        f, csv_path = tempfile.mkstemp()
        open(csv_path, "w").write(csv_data[-1])
        call_command("oscar_import_catalogue", csv_path)
        os.remove(csv_path)


@pytest.fixture(autouse=True)
def mock_suds_client(mocker):
    url = 'https://test.docdatapayments.com/ps/services/paymentservice/1_3?wsdl'

    # create a custom suds client with a wsdl and xsd saved on disk so we don't really connect
    # to docdata
    client = suds.client.Client(
        url, plugins=[DocdataAPIVersionPlugin()], transport=DocdataMockTransport())
    client.options.prettyxml = True

    # patch the CACHED_CLIENT so get_suds_client will return ours
    mocker.patch.dict("oscar_docdata.gateway.CACHED_CLIENT", {url: client})

    return client


@pytest.fixture()
def mock_transport(mock_suds_client):
    return mock_suds_client.options.transport
