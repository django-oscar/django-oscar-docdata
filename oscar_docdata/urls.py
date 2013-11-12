from django.conf.urls import patterns, url
from .views import OrderReturnView, StatusChangedNotificationView


urlpatterns = patterns('',
    url(r'^return/$', OrderReturnView.as_view(), name='return_url'),
    url(r'^update_order/$', StatusChangedNotificationView.as_view(), name='status_changed'),
)
