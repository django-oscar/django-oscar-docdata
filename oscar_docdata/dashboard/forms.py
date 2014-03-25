from django import forms
from django.utils.translation import ugettext_lazy as _
from oscar_docdata.models import DocdataOrder


class DocdataOrderSearchForm(forms.Form):
    order_number = forms.CharField(required=False, label=_("Order number"))
    order_status = forms.ChoiceField(required=False, label=_("Status"), choices=(('', '---------'),) + DocdataOrder.STATUS_CHOICES)
