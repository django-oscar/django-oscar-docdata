from django.dispatch import Signal

order_status_changed = Signal(providing_args=["order", "old_status", "new_status"])
