from django.contrib import admin
from oscar_docdata.models import DocdataOrder, DocdataPayment


class DocdataPaymentInline(admin.TabularInline):
    model = DocdataPayment
    readonly_fields = ('payment_id', 'status', 'payment_method')


class DocdataOrderAdmin(admin.ModelAdmin):
    """
    Admin for .
    """
    list_display = ('merchant_order_id', 'order_key', 'total_gross_amount', 'status', 'created')
    inlines = (DocdataPaymentInline,)

    readonly_fields = (
        'merchant_order_id', 'order_key', 'total_gross_amount', 'status', 'language', 'currency', 'country',
    )


admin.site.register(DocdataOrder, DocdataOrderAdmin)
