from six import text_type


class OrderKeyMissing(ValueError):
    """
    Missing an order key!
    """

class InvalidMerchant(ValueError):
    """
    Provided order belongs to a different merchant!
    """

class DocdataException(Exception):
    """
    Base class for all exceptions from Docdata
    """
    def __init__(self, code, value):
        super(DocdataException, self).__init__(value)
        self.code = code
        self.value = text_type(value)


class DocdataCreateError(DocdataException):
    """
    There was an error creating the payment.
    """


class DocdataStartError(DocdataException):
    """
    There was an error start the payment..
    """


class DocdataStatusError(DocdataException):
    """
    There was an error requesting the status
    """


class DocdataCancelError(DocdataException):
    """
    There was an error cancelling the order.
    """
