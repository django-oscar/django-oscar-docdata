import logging
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from django.db import transaction
from oscar_docdata.exceptions import DocdataStatusError
from oscar_docdata.facade import get_facade
from oscar_docdata.models import DocdataOrder


class Command(BaseCommand):
    help = "Update the status of the given orders"
    option_list = (
        make_option('--all', action='store_true', dest='all', default=False,
            help="Update all orders"),
        make_option('--status', action='store', dest='status', default=None,
            help="Update all orders of a given status"),
    ) + BaseCommand.option_list


    def handle(self, *args, **options):
        """
        Update the status.
        """
        # At -v2 SOAP requests are outputted.
        do_all = options['all']
        only_status = options['status']
        verbosity = int(options['verbosity'])

        # Apply verbosity
        logging.getLogger('oscar_docdata.interface').setLevel('WARNING' if verbosity < 2 else 'DEBUG')
        logging.getLogger('suds.transport').setLevel('INFO' if verbosity < 3 else 'DEBUG')

        qs = DocdataOrder.objects.active_merchants()
        facade = get_facade()

        if do_all:
            orders = qs.all()

            if only_status:
                orders = orders.filter(status=only_status)

            if args:
                raise CommandError("No order numbers have to be provided for --all")
        else:
            if not args:
                raise CommandError("Expected order numbers as argument")

            # First get all orders, check them.
            orders = []
            for order_number in args:
                try:
                    order = qs.get(merchant_order_id=order_number)
                except DocdataOrder.DoesNotExist:
                    self.stderr.write(u"- Order does not exist: {0}\n".format(order_number))
                    continue
                else:
                    if only_status and order.status != only_status:
                        self.stderr.write(u"- Order {0} does not have status {1}, but {2}\n".format(order_number, only_status, order.status))
                        continue
                    orders.append(order)

        for order in orders:
            self.stdout.write(u"- Checking {0}\n".format(order.merchant_order_id))

            with transaction.atomic():
                # First request the order at docdata, avoid expiring an order which missed an update (very unlikely)
                old_status = order.status
                try:
                    facade.update_order(order)
                except DocdataStatusError as e:
                    self.stderr.write(u"{0}\n".format(e))
                    continue

                if order.status == old_status:
                    self.stderr.write(u"  Order {0} status unchanged, remained: {1}".format(order.merchant_order_id, order.status))
                else:
                    self.stdout.write(u"  Order {0} status changed from {1} to {2}".format(order.merchant_order_id, old_status, order.status))
