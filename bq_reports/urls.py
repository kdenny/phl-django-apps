from django.conf.urls import url

from bq_reports import views

urlpatterns = [
    url(r'^reports/adblock_revenue/$', views.AdblockRevenue.as_view()),
    url(r'^reports/traffic_breakdown/$', views.TrafficBreakdown.as_view()),
    url(r'^reports/content_analytics/$', views.ContentAnalytics.as_view())
]