from datetime import timedelta
import logging
from optparse import make_option
from django.core.management.base import NoArgsCommand
from django.db import transaction
from django.utils.timezone import now
from oscar_docdata.facade import get_facade
from oscar_docdata.models import DocdataOrder


class Command(NoArgsCommand):
    help = "Mark old open orders as expired"
    option_list = (
        make_option('-p', '--dry-run', action='store_true', dest='dry-run', default=False,
            help="Only list what will change, don't make the actual changes"),
    ) + NoArgsCommand.option_list

    def handle_noargs(self, **options):
        """
        Update the status.
        """
        is_dry_run = options.get('dry-run', False)
        expire_status_choices = (DocdataOrder.STATUS_NEW, DocdataOrder.STATUS_IN_PROGRESS)

        # At -v2 SOAP requests are outputted.
        verbosity = int(options['verbosity'])
        logging.getLogger('suds.transport').setLevel('INFO' if verbosity < 2 else 'DEBUG')

        qs = DocdataOrder.objects.active_merchants() \
            .filter(status__in=expire_status_choices) \
            .filter(created__lt=(now() - timedelta(days=21)))  # 3 weeks, based on manual testing.

        facade = get_facade()

        if is_dry_run:
            self.stdout.write(u"Expiring orders (DRY-RUN):")
        else:
            self.stdout.write(u"Expiring orders:")

        for order in qs.iterator():
            # Will loop through all one by one, so signals can be properly fired:
            self.stdout.write(u"- {0}\t(created {1:%Y-%m-%d}, still {2})".format(order.merchant_order_id, order.created, order.status))

            # Will update
            old_status = order.status
            order.status = DocdataOrder.STATUS_EXPIRED

            if not is_dry_run:
                with transaction.atomic():
                    # First request the order at docdata, avoid expiring an order which missed an update (very unlikely)
                    facade.update_order(order)
                    if order.status not in expire_status_choices:
                        if order.status == DocdataOrder.STATUS_EXPIRED:
                            self.stdout.write(u"  Updated order {0} via status API, detected expired state".format(order.merchant_order_id))
                        else:
                            self.stderr.write(u"  Skipping order {0}, status changed to: {1}".format(order.merchant_order_id, order.status))
                    else:
                        # More efficient SQL
                        DocdataOrder.objects.filter(id=order.id).update(status=DocdataOrder.STATUS_EXPIRED)

                        try:
                            # Make sure Oscar is updated, and the signal is sent.
                            facade.order_status_changed(order, old_status, order.status)
                        except Exception as e:
                            self.stderr.write(u"Failed to update order {0}: {1}".format(order.id, e))
                            DocdataOrder.objects.filter(id=order.id).update(status=old_status)
