from datetime import datetime
from optparse import make_option
from django.core.management.base import NoArgsCommand, CommandError
from django.db.models import Sum
from django.utils.timezone import now, get_current_timezone
from oscar_docdata.models import DocdataOrder


class Command(NoArgsCommand):
    help = "Show the monthly order statistics"
    option_list = (
        make_option('-s', '--status', action='store', dest='status', default='',
            help="Which status to use, defaults to 'paid'"),
    ) + NoArgsCommand.option_list

    def handle_noargs(self, **options):
        """
        Update the status.
        """
        status = options.get('status', DocdataOrder.STATUS_PAID)
        all_status_choices = dict(DocdataOrder.STATUS_CHOICES).keys()
        if status and status not in all_status_choices:
            raise CommandError("Invalid status, valid choices are: {0}".format(", ".join(sorted(all_status_choices))))

        base_qs = DocdataOrder.objects.current_merchant()

        try:
            start_date = base_qs.values_list('created', flat=True).order_by('created')[0]
        except IndexError:
            self.stdout.write("No orders available")

        currencies = list(base_qs.values_list('currency', flat=True).order_by('currency').distinct())

        tzinfo = get_current_timezone()
        cur_date = datetime(start_date.year, start_date.month, 1, tzinfo=tzinfo)
        end_date = now()

        col_style = "| {0:8} | {1:3} | {2:12} | {3:12} | {4:12} | {5:12} | {6:12} |"
        header = col_style.format("Month", "Cur", "Registrered", "Captured", "Difference", "Refunded", "Charged back")
        sep = '-' * len(header)
        self.stdout.write(sep)
        self.stdout.write(header)
        self.stdout.write(sep)

        next_date = None

        while cur_date < end_date:
            if next_date and len(currencies) > 1:
                self.stdout.write(col_style.format('', '', '', '', '', '', ''))

            if cur_date.month == 12:
                next_date = datetime(cur_date.year + 1, 1, 1, tzinfo=tzinfo)
            else:
                next_date = datetime(cur_date.year, cur_date.month + 1, 1, tzinfo=tzinfo)

            qs = base_qs.filter(created__range=(cur_date, next_date))
            if status:
                qs = qs.filter(status=status)

            for currency in currencies:
                totals = qs.filter(currency=currency).aggregate(
                    cap=Sum('total_captured'),
                    reg=Sum('total_registered'),
                    ref=Sum('total_refunded'),
                    cb=Sum('total_charged_back'),
                )

                self.stdout.write(col_style.format(
                    "{0}-{1:02d}".format(cur_date.year, cur_date.month),
                    currency,
                    totals['cap'] or 0,
                    totals['reg'] or 0,
                    (totals['cap'] or 0) - (totals['reg'] or 0) or '',
                    totals['ref'] or 0,
                    totals['cb'] or 0,
                ))

            cur_date = next_date
