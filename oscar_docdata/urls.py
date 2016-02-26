from django.conf.urls import url
from .views import OrderReturnView, StatusChangedNotificationView


urlpatterns = [
    url(r'^return/$', OrderReturnView.as_view(), name='return_url'),
    url(r'^update_order/$', StatusChangedNotificationView.as_view(), name='status_changed'),
]
