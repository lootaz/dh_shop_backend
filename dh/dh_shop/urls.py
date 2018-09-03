from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'shops', views.ShopViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'time_ranges', views.TimeRangeViewSet)

urlpatterns = [
    url(r'api/', include(router.urls)),
    url(r'api/login/$', views.login),
    url(r'api/logout/$', views.logout),
    url(r'api/register/$', views.register),
    url(r'api/users/(?P<pk>[0-9]+)/$', views.UserView.as_view())

]
