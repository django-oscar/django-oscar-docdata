"""
Django compatibility features
"""

__all__ = (
    'transaction_atomic',
)

# New transaction support in Django 1.6
from django.db import transaction
try:
    transaction_atomic = transaction.atomic
except AttributeError:
    transaction_atomic = transaction.commit_on_success
