from django.dispatch import Signal

# The signal which is fired on order status changes.
# You should handle this signal to create the payment Source records in Oscar.
order_status_changed = Signal(providing_args=["order", "old_status", "new_status"])


payment_updated = Signal(providing_args=['order', 'payment'])

payment_added = Signal(providing_args=['order', 'payment'])

return_view_called = Signal(providing_args=['request', 'order', 'callback'])

status_changed_view_called = Signal(providing_args=['request', 'order'])
