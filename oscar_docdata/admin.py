from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from oscar_docdata.facade import Facade
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

    def get_urls(self):
        urls = super(DocdataOrderAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.module_name

        return patterns('',
            url(r'^([^/]+)/update/$', self.admin_site.admin_view(self.update_view), name='%s_%s_update' % info),
        ) + urls

    def update_view(self, request, object_id):
        """
        Fetch the latest status from docdata.
        """
        order = self.get_object(request, unquote(object_id))
        if not self.has_change_permission(request, order):
            raise PermissionDenied

        # Perform update.
        facade = Facade()
        facade.update_order(order)

        self.message_user(request, u"Order status is updated")

        info = self.model._meta.app_label, self.model._meta.module_name
        change_view = 'admin:%s_%s_change' % info
        return HttpResponseRedirect(reverse(change_view, args=(order.pk,)))


admin.site.register(DocdataOrder, DocdataOrderAdmin)
