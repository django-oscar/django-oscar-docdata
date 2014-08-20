"""
Django compatibility features
"""

__all__ = (
    'transaction_atomic',
    'get_model',
)

# New transaction support in Django 1.6
from django.db import transaction
try:
    transaction_atomic = transaction.atomic
except AttributeError:
    transaction_atomic = transaction.commit_on_success

# Oscar 0.7 get_model code
try:
    from oscar.core.loading import get_model
except ImportError:
    from django.db.models import get_model
