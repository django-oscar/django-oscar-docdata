import logging
from django.core.management.base import BaseCommand, CommandError

from django.db import transaction
from oscar_docdata.facade import get_facade
from oscar_docdata.models import DocdataOrder


class Command(BaseCommand):
    help = "Update the status of the given orders"

    def handle(self, *args, **options):
        """
        Update the status.
        """
        # At -v2 SOAP requests are outputted.
        verbosity = int(options['verbosity'])
        logging.getLogger('suds.transport').setLevel('INFO' if verbosity < 2 else 'DEBUG')

        if not args:
            raise CommandError("Expected order numbers as argument")

        qs = DocdataOrder.objects.active_merchants()

        facade = get_facade()

        for order_number in args:
            try:
                order = qs.get(merchant_order_id=order_number)
            except DocdataOrder.DoesNotExist:
                self.stderr.write(u"- Order does not exist: {0}\n".format(order_number))
                continue

            self.stdout.write(u"- Checking {0}\n".format(order_number))

            with transaction.atomic():
                # First request the order at docdata, avoid expiring an order which missed an update (very unlikely)
                old_status = order.status
                facade.update_order(order)
                if order.status == old_status:
                    self.stderr.write(u"  Order {0} status unchanged, remained: {1}".format(order.merchant_order_id, order.status))
                else:
                    self.stdout.write(u"  Order {0} status changed from {1} to {2}".format(order.merchant_order_id, old_status, order.status))
