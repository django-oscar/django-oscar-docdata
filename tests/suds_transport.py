import os

import pytest

from six.moves import http_client

import suds


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
WSDL = open(os.path.join(CURRENT_DIR, "testdata", "wsdl-1_3.wsdl")).read()
XSD = open(os.path.join(CURRENT_DIR, "testdata", "xsd1-1_3.xsd")).read()


class DocdataMockTransport(suds.transport.Transport):

    # this will be set with the different fixtures
    responses = None

    def set_responses(self, responses=[]):
        self.responses = (x for x in responses)

    def get_response(self):
        for response in self.responses:
            yield response

    def open(self, request):
        if "?wsdl" in request.url:
            return suds.BytesIO(suds.byte_str(WSDL))
        elif "?xsd" in request.url:
            return suds.BytesIO(suds.byte_str(XSD))

        pytest.fail("No supported open request url: {}".format(request.url))

    def send(self, request):
        if 'SOAPAction' in request.headers:
            if self.responses is None:
                pytest.fail("No responses set with mock_transport.set_responses()")
            try:
                response = next(self.responses)
            except StopIteration:
                pytest.fail(
                    "Not enought responses available set with mock_transport.set_responses()")

            return suds.transport.Reply(
                http_client.OK, {}, suds.byte_str(response))

        pytest.fail("No SOAPAction header in request {}".format(request.headers))
