from django.conf.urls import patterns, url
from oscar.core.application import Application
from . import views


class DocdataOrderDashboardApplication(Application):
    name = None
    default_permissions = ['is_staff', ]

    list_view = views.DocdataOrderListView
    detail_view = views.DocdataOrderDetailView
    update_status_view = views.DocdataOrderUpdateStatusView
    cancel_view = views.DocdataOrderCancelView

    def get_urls(self):
        """
        Get URL patterns defined for flatpage management application.
        """
        urls = [
            url(r'^$', self.list_view.as_view(), name='docdata-order-list'),
            url(r'^detail/(?P<pk>[-\w]+)/$', self.detail_view.as_view(), name='docdata-order-detail'),
            url(r'^update-status/(?P<pk>[-\w]+)/$', self.update_status_view.as_view(), name='docdata-order-update-status'),
            url(r'^cancel/(?P<pk>[-\w]+)/$', self.cancel_view.as_view(), name='docdata-order-cancel'),
        ]
        return self.post_process_urls(patterns('', *urls))


application = DocdataOrderDashboardApplication()
