from django.dispatch import Signal

# The signal which is fired on order status changes.
# You should handle this signal to create the payment Source records in Oscar.
order_status_changed = Signal(providing_args=["order", "old_status", "new_status"])


payment_added = Signal(providing_args=['order', 'payment'])

payment_updated = Signal(providing_args=['order', 'payment'])