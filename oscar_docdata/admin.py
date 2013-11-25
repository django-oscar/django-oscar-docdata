from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from oscar_docdata.exceptions import DocdataCancelError, DocdataStatusError
from oscar_docdata.facade import Facade
from oscar_docdata.models import DocdataOrder, DocdataPayment


class DocdataPaymentInline(admin.TabularInline):
    model = DocdataPayment
    readonly_fields = (
        'payment_id',
        'status',
        'amount_debited',
        'amount_refunded',
        'amount_chargeback',
        'payment_method',
        'confidence_level',
    )
    extra = 0
    can_delete = False

    def has_add_permission(self, request):
        return False


class DocdataOrderAdmin(admin.ModelAdmin):
    """
    Admin for .
    """
    list_display = ('merchant_order_id', 'order_key', 'total_gross_amount', 'status', 'created')
    list_filter = ('status',)
    inlines = (DocdataPaymentInline,)
    date_hierarchy = 'created'

    cancel_confirmation_template = None

    edit_readonly_fields = (
        'merchant_order_id', 'order_key', 'total_gross_amount', 'currency', 'status', 'language', 'country',
        'total_registered',
        'total_shopper_pending',
        'total_acquirer_pending',
        'total_acquirer_approved',
        'total_captured',
        'total_refunded',
        'total_charged_back',
    )
    fieldsets = (
        (None, {
            'fields': (
                'merchant_order_id', 'order_key', 'total_gross_amount', 'currency', 'status', 'language', 'country',
            ),
            'classes': ('wide',),
        }),
        (_("Amounts"), {
            'fields': (
                'total_registered',
                'total_shopper_pending',
                'total_acquirer_pending',
                'total_acquirer_approved',
                'total_captured',
                'total_refunded',
                'total_charged_back',
            ),
            'classes': ('wide',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pk:
            return self.edit_readonly_fields
        else:
            return self.readonly_fields

    def get_urls(self):
        urls = super(DocdataOrderAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.module_name

        return patterns('',
            url(r'^([^/]+)/update/$', self.admin_site.admin_view(self.update_view), name='%s_%s_update' % info),
            url(r'^([^/]+)/cancel/$', self.admin_site.admin_view(self.cancel_view), name='%s_%s_cancel' % info),
        ) + urls

    def update_view(self, request, object_id):
        """
        Fetch the latest status from docdata.
        """
        opts = self.model._meta
        order = self.get_object(request, unquote(object_id))
        if not self.has_change_permission(request, order):
            raise PermissionDenied
        if order is None:
            raise Http404("No order found!")

        # Perform update.
        try:
            facade = Facade()
            facade.update_order(order)
        except DocdataStatusError as e:
            self.message_user(request, e.value, level=messages.ERROR)
            return HttpResponseRedirect(reverse('admin:%s_%s_change' % (opts.app_label, opts.module_name), args=(object_id,), current_app=self.admin_site.name))
        else:
            self.message_user(request, u"Order status is updated")

        info = self.model._meta.app_label, self.model._meta.module_name
        change_view = 'admin:%s_%s_change' % info
        return HttpResponseRedirect(reverse(change_view, args=(order.pk,)))

    def has_cancel_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm('{0}.cancel_{1}'.format(opts.app_label, opts.object_name.lower()))

    @csrf_protect_m
    def cancel_view(self, request, object_id, extra_context=None):
        opts = self.model._meta
        app_label = opts.app_label

        obj = self.get_object(request, unquote(object_id))
        if not self.has_cancel_permission(request, obj):
            raise PermissionDenied
        if obj is None:
            raise Http404("No order found!")

        if request.POST: # The user has already confirmed the deletion.
            obj_display = force_text(obj)
            try:
                self.cancel_order(request, obj)
            except DocdataCancelError as e:
                self.message_user(request, e.value, level=messages.ERROR)
                return HttpResponseRedirect(reverse('admin:%s_%s_change' % (opts.app_label, opts.module_name), args=(object_id,), current_app=self.admin_site.name))
            else:
                self.message_user(request, _('The %(name)s "%(obj)s" was cancelled successfully.') % {'name': force_text(opts.verbose_name), 'obj': force_text(obj_display)})

            if not self.has_change_permission(request, None):
                return HttpResponseRedirect(reverse('admin:index', current_app=self.admin_site.name))
            return HttpResponseRedirect(reverse('admin:%s_%s_changelist' % (opts.app_label, opts.module_name), current_app=self.admin_site.name))

        object_name = force_text(opts.verbose_name)

        context = {
            "title": _("Are you sure?"),
            "object_name": object_name,
            "object": obj,
            "opts": opts,
            "app_label": app_label,
        }
        context.update(extra_context or {})

        return TemplateResponse(request, self.cancel_confirmation_template or [
            "admin/%s/%s/cancel_confirmation.html" % (app_label, opts.object_name.lower()),
            "admin/%s/cancel_confirmation.html" % app_label,
            "admin/cancel_confirmation.html"
        ], context, current_app=self.admin_site.name)

    def cancel_order(self, request, obj):
        """
        Cancel an existing order in the system.
        """
        facade = Facade()
        facade.cancel_order(obj)


admin.site.register(DocdataOrder, DocdataOrderAdmin)
